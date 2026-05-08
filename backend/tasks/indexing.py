import json
import time
import uuid

from celery_app import celery_app
from core.config import config
from services.pdf import extract_text
from services.chunking import chunk_text
from services.embedding import get_embeddings_batch
from services.vector_store import upsert_vectors
from db.database import SessionLocal
from db.models import Document


@celery_app.task(bind=True, name="tasks.indexing.index_document")
def index_document(self, file_bytes: bytes, filename: str, doc_id: str, user_id: int):
    """
    Background task: extract → chunk → embed → store in Qdrant + Postgres.
    Called by the upload route after saving the file.
    """
    try:
        # 1. Extract text from bytes
        import io
        file_obj = io.BytesIO(file_bytes)
        pages = extract_text(file_obj, filename)

        # 2. Chunk
        chunks = chunk_text(pages, doc_id, filename)

        # 3. Embed (cached inside get_embeddings_batch via cache.py)
        texts = [c["text"] for c in chunks]
        embeddings = get_embeddings_batch(texts)

        # 4. Store vectors in Qdrant
        upsert_vectors(chunks, embeddings, doc_id, user_id)

        # 5. Update document status in Postgres
        db = SessionLocal()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                doc.status = "ready"
                doc.chunk_count = len(chunks)
                db.commit()
        finally:
            db.close()

        return {"status": "success", "doc_id": doc_id, "chunks": len(chunks)}

    except Exception as exc:
        # Mark as failed in DB
        db = SessionLocal()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                doc.status = "failed"
                db.commit()
        finally:
            db.close()
        raise self.retry(exc=exc, countdown=5, max_retries=3)