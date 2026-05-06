import pytest
from services.chunking import chunk_text


PAGES = [
    {"page": 1, "text": "Hello world. " * 50},
    {"page": 2, "text": "Second page content. " * 30},
]


def test_chunk_count():
    chunks = chunk_text(PAGES, "doc-1", "test.pdf", chunk_size=100)
    assert len(chunks) > 0


def test_chunk_size_respected():
    chunks = chunk_text(PAGES, "doc-1", "test.pdf", chunk_size=100)
    for c in chunks:
        assert len(c["text"]) <= 100


def test_chunk_metadata():
    chunks = chunk_text(PAGES, "doc-42", "my_file.pdf", chunk_size=200)
    for c in chunks:
        assert c["doc_id"] == "doc-42"
        assert c["fileName"] == "my_file.pdf"
        assert c["page"] in (1, 2)
        assert "text" in c


def test_empty_pages():
    chunks = chunk_text([], "doc-1", "empty.pdf")
    assert chunks == []


def test_page_assignment():
    pages = [{"page": 5, "text": "A" * 600}]
    chunks = chunk_text(pages, "doc-1", "f.pdf", chunk_size=500)
    assert all(c["page"] == 5 for c in chunks)