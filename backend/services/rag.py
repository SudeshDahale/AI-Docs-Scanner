import os
import faiss
import json
import numpy as np
from services.llm import get_embedding, client

# -----------------------------
# STORAGE PATHS
# -----------------------------
BASE_DIR = "storage"
INDEX_DIR = os.path.join(BASE_DIR, "indexes")
CHUNK_DIR = os.path.join(BASE_DIR, "chunks")

os.makedirs(INDEX_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)


# -----------------------------
# 1. CHUNKING (page-aware)
# Chunks are dicts: {text, page, doc_id, fileName}
# -----------------------------
def chunk_text(pages, doc_id, file_name, chunk_size=500):
    """
    pages: list of {page: int, text: str}
    Returns list of chunk dicts with page metadata.
    """
    chunks = []
    for page_obj in pages:
        page_num = page_obj["page"]
        text = page_obj["text"]
        for i in range(0, len(text), chunk_size):
            chunks.append({
                "text": text[i:i + chunk_size],
                "page": page_num,
                "doc_id": doc_id,
                "fileName": file_name,
            })
    return chunks


# -----------------------------
# 2. CREATE VECTOR STORE
# -----------------------------
def create_vector_store(chunks, doc_id):
    if not chunks:
        raise ValueError("No chunks found for document")

    embeddings = [get_embedding(c["text"]) for c in chunks]

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

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
# 4. LOAD CHUNKS
# -----------------------------
def load_chunks(doc_id):
    path = f"{CHUNK_DIR}/{doc_id}.json"
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


# -----------------------------
# 5. SEARCH — returns chunk dicts
# -----------------------------
def search(index, query, chunks, k=3):
    query_embedding = get_embedding(query)
    D, I = index.search(
        np.array([query_embedding]).astype("float32"), k
    )
    results = []
    for i in I[0]:
        if 0 <= i < len(chunks):
            results.append(chunks[i])
    return results


# -----------------------------
# 6. MULTI-DOC SEARCH
# -----------------------------
def search_multiple(doc_ids, query, k=3):
    all_chunks = []
    for doc_id in doc_ids:
        index = load_vector_store(doc_id)
        chunks = load_chunks(doc_id)
        if index is None or chunks is None:
            continue
        results = search(index, query, chunks, k=k)
        all_chunks.extend(results)
    return all_chunks


# -----------------------------
# 7. ANSWER WITH CITATIONS
# Returns {answer: str, citations: [{page, fileName, snippet}]}
# -----------------------------
def answer_question(query, context_chunks, history=None):
    # Build numbered context so the LLM can cite by number
    context_parts = []
    for i, chunk in enumerate(context_chunks):
        context_parts.append(
            f"[{i+1}] (File: {chunk['fileName']}, Page {chunk['page']})\n{chunk['text']}"
        )
    context = "\n\n".join(context_parts)

    # System prompt
    messages = [
        {
            "role": "system",
            "content": (
                "You are a document assistant. Answer using ONLY the provided document context. "
                "When you use information from a source, cite it inline using [1], [2], etc. "
                "matching the numbers in the context. Be concise and accurate. "
                "You have access to the conversation history to answer follow-up questions."
            )
        }
    ]

    # Inject prior turns (cap at last 10 to stay within token limits)
    if history:
        for turn in history[-10:]:
            messages.append({"role": turn["role"], "content": turn["content"]})

    # Current question with fresh context
    messages.append({
        "role": "user",
        "content": f"Document context:\n{context}\n\nQuestion: {query}"
    })

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    answer = response.choices[0].message.content

    # Build deduplicated citations list preserving order
    seen = set()
    citations = []
    for chunk in context_chunks:
        key = (chunk["doc_id"], chunk["page"])
        if key not in seen:
            seen.add(key)
            citations.append({
                "page": chunk["page"],
                "fileName": chunk["fileName"],
                "snippet": chunk["text"][:200].strip(),
            })

    return {"answer": answer, "citations": citations}