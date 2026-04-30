import os
from openai import OpenAI
from dotenv import load_dotenv
import faiss
import numpy as np

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize(text):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Summarize the document clearly."},
            {"role": "user", "content": text[:3000]}
        ]
    )
    return response.choices[0].message.content

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def create_vector_store(chunks):
    embeddings = [get_embedding(chunk) for chunk in chunks]

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)

    index.add(np.array(embeddings).astype("float32"))

    return index, chunks

def search(index, query, chunks, k=3):
    query_embedding = get_embedding(query)

    D, I = index.search(
        np.array([query_embedding]).astype("float32"), k
    )

    results = [chunks[i] for i in I[0]]
    return results

def answer_question(query, context_chunks):
    context = "\n".join(context_chunks)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Answer based only on the context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
    )

    return response.choices[0].message.content