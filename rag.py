import os
from dotenv import load_dotenv
import json
from langchain_openai import OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter


load_dotenv()

# Load your docs
with open("data/cfpb_docs.json") as f:
    docs = json.load(f)

# Break each doc into smaller chunks 
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,      
    chunk_overlap=50,    
    separators=["\n\n", "\n", ". ", " ", ""]  
)

#Turn docs into langchain documents
documents = []
for doc in docs:
    text = doc.get("answer", "")
    chunks = text_splitter.split_text(text)
    for chunk in chunks:
        documents.append(Document(
            page_content=chunk,
            metadata={"source": doc.get("url", "unknown")}
        ))

for i, doc in enumerate(documents[:5]):  # show first 5
    print(f"\n--- Chunk {i} ---")
    print(doc.page_content)
    print("Source:", doc.metadata["source"])
        
# Embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Build FAISS vectorstore
vectorstore = FAISS.from_documents(documents, embeddings)

# Retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Claude 3 haiku LLM
llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0.3, max_tokens=300)

# Chain to inject relevant documents into LLM prompt
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",   
    return_source_documents=True
)


if __name__ == "__main__":
    question = "What happens if I don't pay my loans on time?"
    result = qa_chain.invoke({"query": question})

    print("\nQUESTION:", question)
    print("\nANSWER:", result["result"])
    print("\nSOURCES:", [doc.metadata["source"] for doc in result["source_documents"]])