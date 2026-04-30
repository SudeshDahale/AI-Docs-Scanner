import os
import faiss
import json
import numpy as np
from services.llm import get_embedding, client

# -----------------------------
# STORAGE PATHS (centralized)
# -----------------------------
BASE_DIR = "storage"
INDEX_DIR = os.path.join(BASE_DIR, "indexes")
CHUNK_DIR = os.path.join(BASE_DIR, "chunks")

os.makedirs(INDEX_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)


# -----------------------------
# 1. CHUNKING
# -----------------------------
def chunk_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


# -----------------------------
# 2. CREATE VECTOR STORE
# -----------------------------
def create_vector_store(chunks, doc_id):
    if not chunks:
        raise ValueError("No chunks found for document")

    embeddings = [get_embedding(chunk) for chunk in chunks]

    dim = len(embeddings[0])

    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

    # save index
    faiss.write_index(index, f"{INDEX_DIR}/{doc_id}.index")

    return index, chunks


# -----------------------------
# 3. LOAD VECTOR STORE
# -----------------------------
def load_vector_store(doc_id):
    path = f"{INDEX_DIR}/{doc_id}.index"

    if not os.path.exists(path):
        return None

    return faiss.read_index(path)


# -----------------------------
# 4. SAVE CHUNKS
# -----------------------------
def save_chunks(doc_id, chunks):
    path = f"{CHUNK_DIR}/{doc_id}.json"

    with open(path, "w") as f:
        json.dump(chunks, f)


# -----------------------------
# 5. LOAD CHUNKS
# -----------------------------
def load_chunks(doc_id):
    path = f"{CHUNK_DIR}/{doc_id}.json"

    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        return json.load(f)


# -----------------------------
# 6. SEARCH
# -----------------------------
def search(index, query, chunks, k=3):
    query_embedding = get_embedding(query)

    D, I = index.search(
        np.array([query_embedding]).astype("float32"),
        k
    )

    results = []
    for i in I[0]:
        if 0 <= i < len(chunks):   # safety check
            results.append(chunks[i])

    return results


# -----------------------------
# 7. ANSWER GENERATION
# -----------------------------
def answer_question(query, context_chunks):
    context = "\n".join(context_chunks)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Answer strictly using only the provided context."
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }
        ]
    )

    return response.choices[0].message.content