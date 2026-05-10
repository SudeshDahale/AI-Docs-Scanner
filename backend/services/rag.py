from services.chunking import chunk_text
from services.embedding import get_embeddings_batch
from services.retrieval import (
    build_vector_store,
    load_vector_store,
    load_chunks,
    search,
    search_multiple,
)
from services.generation import answer_question
import os
import numpy as np
from core.config import config

os.makedirs(config.index_dir, exist_ok=True)
os.makedirs(config.chunk_dir, exist_ok=True)


def create_vector_store(chunks, doc_id):
    texts = [c["text"] for c in chunks]
    embeddings = get_embeddings_batch(texts)
    return build_vector_store(chunks, doc_id, embeddings), chunks


__all__ = [
    "chunk_text",
    "create_vector_store",
    "load_vector_store",
    "load_chunks",
    "search",
    "search_multiple",
    "answer_question",
]