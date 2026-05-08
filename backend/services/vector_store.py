"""
Qdrant-backed vector store — replaces FAISS flat files.
"""
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams,
    PointStruct, Filter, FieldCondition, MatchValue,
)
from core.config import config

_client: QdrantClient = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=config.QDRANT_URL)
        _ensure_collection()
    return _client


def _ensure_collection():
    c = _client
    existing = [col.name for col in c.get_collections().collections]
    if config.QDRANT_COLLECTION not in existing:
        c.create_collection(
            collection_name=config.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=config.VECTOR_DIM,
                distance=Distance.COSINE,
            ),
        )


def upsert_vectors(
    chunks: List[Dict],
    embeddings: List[List[float]],
    doc_id: str,
    user_id: int,
) -> None:
    """Store chunk embeddings in Qdrant with doc_id + user_id payload."""
    client = get_client()
    points = [
        PointStruct(
            id=str(abs(hash(f"{doc_id}:{i}")) % (2**63)),
            vector=embeddings[i],
            payload={
                "doc_id": doc_id,
                "user_id": user_id,
                "text": chunks[i]["text"],
                "page": chunks[i].get("page", i),
                "fileName": chunks[i].get("fileName", ""),
                "chunk_index": i,
            },
        )
        for i in range(len(chunks))
    ]
    client.upsert(collection_name=config.QDRANT_COLLECTION, points=points)


def search_vectors(
    query_embedding: List[float],
    doc_ids: List[str],
    user_id: int,
    top_k: int = None,
) -> List[Dict]:
    """Semantic search filtered to specific docs owned by this user."""
    top_k = top_k or config.RETRIEVAL_TOP_K
    client = get_client()

    results = client.search(
        collection_name=config.QDRANT_COLLECTION,
        query_vector=query_embedding,
        query_filter=Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
            ]
        ),
        limit=top_k * 3,  # fetch extra, filter by doc_ids below
    )

    chunks = []
    for hit in results:
        p = hit.payload
        if p["doc_id"] in doc_ids:
            chunks.append({
                "text": p["text"],
                "doc_id": p["doc_id"],
                "page": p["page"],
                "fileName": p["fileName"],
                "score": hit.score,
            })
        if len(chunks) >= top_k:
            break
    return chunks


def delete_document_vectors(doc_id: str, user_id: int) -> None:
    """Remove all vectors for a document."""
    client = get_client()
    client.delete(
        collection_name=config.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[
                FieldCondition(key="doc_id", match=MatchValue(value=doc_id)),
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
            ]
        ),
    )