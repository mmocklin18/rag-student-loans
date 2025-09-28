import os
from dotenv import load_dotenv
import json
from langchain_openai import OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA

load_dotenv()

# Load your docs
with open("data/cfpb_docs.json") as f:
    docs = json.load(f)

# Break each doc into smaller chunks TODO: Split into chunks at paragraph / sentence ends
def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

#Turn docs into langchain documents
documents = []
for doc in docs:
   for chunk in chunk_text(doc["answer"]):
        documents.append(Document(
            page_content=chunk,
            metadata={
                "source": doc.get("url", "unknown")
            }))
        
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
    question = "What are perkins loans"
    result = qa_chain.invoke({"query": question})

    print("\nQUESTION:", question)
    print("\nANSWER:", result["result"])
    print("\nSOURCES:", [doc.metadata["source"] for doc in result["source_documents"]])