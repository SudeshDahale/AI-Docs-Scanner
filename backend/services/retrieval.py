import os
import json
import numpy as np
import faiss
from typing import List, Dict, Optional, Tuple
from openai import OpenAI

from core.config import config
from services.embedding import get_embedding


def build_vector_store(
    chunks: List[Dict],
    doc_id: str,
    embeddings: List[List[float]],
) -> faiss.IndexFlatL2:
    """
    Build and persist a FAISS index from pre-computed embeddings.

    Args:
        chunks: chunk dicts (used for length validation)
        doc_id: used to name the index file
        embeddings: vectors aligned with chunks

    Returns:
        the FAISS index
    """
    if not chunks:
        raise ValueError("No chunks provided")
    if len(chunks) != len(embeddings):
        raise ValueError("chunks and embeddings length mismatch")

    os.makedirs(config.index_dir, exist_ok=True)

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings, dtype="float32"))

    index_path = os.path.join(config.index_dir, f"{doc_id}.index")
    faiss.write_index(index, index_path)

    return index


def load_vector_store(doc_id: str) -> Optional[faiss.IndexFlatL2]:
    """Load a persisted FAISS index, or None if it doesn't exist."""
    path = os.path.join(config.index_dir, f"{doc_id}.index")
    if not os.path.exists(path):
        return None
    return faiss.read_index(path)


def load_chunks(doc_id: str) -> Optional[List[Dict]]:
    """Load persisted chunk JSON for a document."""
    path = os.path.join(config.chunk_dir, f"{doc_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def search(
    index: faiss.IndexFlatL2,
    query: str,
    chunks: List[Dict],
    k: int = None,
    client: OpenAI = None,
) -> List[Dict]:
    """
    Find the top-k most relevant chunks for a query.

    Args:
        index: FAISS index for one document
        query: user question
        chunks: aligned list of chunk dicts
        k: number of results (defaults to config)
        client: optional OpenAI client for DI

    Returns:
        list of matching chunk dicts
    """
    k = k or config.RETRIEVAL_TOP_K
    query_vec = get_embedding(query, client=client)
    _, indices = index.search(np.array([query_vec], dtype="float32"), k)
    return [chunks[i] for i in indices[0] if 0 <= i < len(chunks)]


def search_multiple(
    doc_ids: List[str],
    query: str,
    k: int = None,
    client: OpenAI = None,
) -> List[Dict]:
    """
    Search across multiple documents and merge results.

    Args:
        doc_ids: list of document UUIDs
        query: user question
        k: results per document
        client: optional OpenAI client for DI

    Returns:
        merged list of chunk dicts
    """
    k = k or config.RETRIEVAL_TOP_K
    all_chunks: List[Dict] = []
    for doc_id in doc_ids:
        index = load_vector_store(doc_id)
        chunks = load_chunks(doc_id)
        if index is None or chunks is None:
            continue
        results = search(index, query, chunks, k=k, client=client)
        all_chunks.extend(results)
    return all_chunks