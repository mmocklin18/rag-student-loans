import os
from dotenv import load_dotenv
from config import CUSTOM_PROMPT_TEMPLATE
import json
from langchain_openai import OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate



load_dotenv()

all_docs = []
# Load docs from data folder
for filename in os.listdir("data/"):
    if filename.endswith(".json"):
        filepath = os.path.join("data/", filename)
        with open(filepath) as f:
            docs = json.load(f)
            all_docs.extend(docs)

# Chunk docs
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,      
    chunk_overlap=50,    
    separators=["\n\n", "\n", ". ", " ", ""]  
)

#Turn docs into langchain documents
documents = []
for doc in all_docs:
    q = doc.get("question", "")
    a = doc.get("answer", "")

    if q:
        text = f"Question: {q}\nAnswer: {a}"
    else:   
        text = a

    chunks = text_splitter.split_text(text)
    for chunk in chunks:
        documents.append(Document(
            page_content=chunk,
            metadata={"source": doc.get("url", "unknown")}
        ))


        
# Embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Build FAISS vectorstore
vectorstore = FAISS.from_documents(documents, embeddings)

# Retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# Claude 3 haiku LLM
llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0.3, max_tokens=300)


CUSTOM_PROMPT = PromptTemplate(
    template=CUSTOM_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

# Chain to inject relevant documents into LLM prompt
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",   
    return_source_documents=True,
    chain_type_kwargs={"prompt": CUSTOM_PROMPT},

)


if __name__ == "__main__":
    question = "How do I pay off my loans if I don't have the money right now?"
    result = qa_chain.invoke({"query": question})

    print("\nQUESTION:", question)
    print("\nANSWER:", result["result"])
    print("\n--- Retrieved Chunks ---")
    for i, d in enumerate(result["source_documents"]):
        print(f"[{i}] Source: {d.metadata['source']}")
        print(d.page_content[:500], "\n")  # preview first 500 chars