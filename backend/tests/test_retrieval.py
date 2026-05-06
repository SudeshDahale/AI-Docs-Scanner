import pytest
import numpy as np
from unittest.mock import MagicMock, patch
import faiss

from services.retrieval import search, search_multiple, build_vector_store


def _make_index(dim=3, n=4):
    """Create a simple in-memory FAISS index with n random vectors."""
    index = faiss.IndexFlatL2(dim)
    vecs = np.random.rand(n, dim).astype("float32")
    index.add(vecs)
    return index


def _make_chunks(n=4):
    return [
        {"text": f"chunk {i}", "page": i + 1, "doc_id": "d1", "fileName": "f.pdf"}
        for i in range(n)
    ]


def test_search_returns_k_results():
    index = _make_index()
    chunks = _make_chunks()
    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1, 0.2, 0.3], index=0)]
    )
    results = search(index, "query", chunks, k=2, client=mock_client)
    assert len(results) == 2


def test_search_results_are_chunk_dicts():
    index = _make_index()
    chunks = _make_chunks()
    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1, 0.2, 0.3], index=0)]
    )
    results = search(index, "query", chunks, k=3, client=mock_client)
    for r in results:
        assert "text" in r
        assert "page" in r


def test_search_multiple_skips_missing_docs():
    with patch("services.retrieval.load_vector_store", return_value=None), \
         patch("services.retrieval.load_chunks", return_value=None):
        results = search_multiple(["missing-id"], "query")
    assert results == []


def test_search_multiple_merges_results():
    index = _make_index()
    chunks = _make_chunks(4)
    mock_client = MagicMock()
    mock_client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1, 0.2, 0.3], index=0)]
    )
    with patch("services.retrieval.load_vector_store", return_value=index), \
         patch("services.retrieval.load_chunks", return_value=chunks):
        results = search_multiple(["id1", "id2"], "query", k=2, client=mock_client)
    # 2 docs × 2 results each = 4
    assert len(results) == 4