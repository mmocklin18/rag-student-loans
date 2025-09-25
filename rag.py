import os
import json
import numpy as np
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer
from transformers import pipeline



with open("data/cfpb_docs.json") as f:
    docs = json.load(f)

# Break each doc into smaller chunks
def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

texts = []
for doc in docs:
    texts.extend(chunk_text(doc["answer"], chunk_size=300, overlap=50))


embedder = SentenceTransformer("all-MiniLM-L6-v2") 
embeddings = embedder.encode(texts, convert_to_numpy=True)


# NumPy cosine similarity search
def search(query, k=1):
    q_emb = embedder.encode([query], convert_to_numpy=True)
    sims = np.dot(embeddings, q_emb.T) / (norm(embeddings, axis=1) * norm(q_emb))
    top_k = sims.argsort()[-k:][::-1]       
    top_k = top_k.flatten().tolist()    
    return [texts[i] for i in top_k]



qa_model = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",  
    device=-1
)


def truncate_context(context, max_words=300):
    words = context.split()
    if len(words) > max_words:
        return " ".join(words[:max_words])
    return context


def answer_query(query, k=3):
    context = "\n\n".join(search(query, k))
    context = truncate_context(context, max_words=300)

    prompt = (
        f"Answer the question using the context below.\n\n"
        f"Question: {query}\n\n"
        f"Context:\n{context}\n\n"
        f"Answer:"
    )
    result = qa_model(prompt, max_new_tokens=200, do_sample=True, temperature=0.3)
    return result[0]["generated_text"]


if __name__ == "__main__":
    question = "What are Perkins loans and what makes them different from normal loans?"
    answer = answer_query(question, k=3)
    print("\nQUESTION:", question)
    print("\nANSWER:", answer)