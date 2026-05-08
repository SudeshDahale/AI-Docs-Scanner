import json
import time
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from db.database import get_db
from db.models import Document, User
from services.cache import get_cached_response, set_cached_response
from services.retrieval import search_multiple_qdrant
from services.reranking import rerank
from services.generation import answer_question
from services.vector_store import delete_document_vectors
from tasks.indexing import index_document

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "pptx", "ppt", "txt", "md"}


# ─── UPLOAD ──────────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    doc_id = str(uuid.uuid4())
    file_bytes = await file.read()

    # Save to Postgres as "processing"
    doc = Document(
        id=doc_id,
        file_name=file.filename,
        user_id=current_user.id,
        status="processing",
    )
    db.add(doc)
    db.commit()

    # Dispatch Celery task
    index_document.delay(file_bytes, file.filename, doc_id, current_user.id)

    return {"message": "Upload queued", "doc_id": doc_id, "status": "processing"}


# ─── UPLOAD STATUS ───────────────────────────────────────────────────────────

@router.get("/documents/{doc_id}/status")
def document_status(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(
        Document.id == doc_id, Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"doc_id": doc_id, "status": doc.status, "chunk_count": doc.chunk_count}


# ─── LIST DOCUMENTS ───────────────────────────────────────────────────────────

@router.get("/documents")
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    return {
        "documents": [
            {
                "doc_id": d.id,
                "fileName": d.file_name,
                "uploadedAt": d.uploaded_at,
                "status": d.status,
            }
            for d in docs
        ]
    }


# ─── DELETE DOCUMENT ─────────────────────────────────────────────────────────

@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(
        Document.id == doc_id, Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    delete_document_vectors(doc_id, current_user.id)
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully"}


# ─── RENAME DOCUMENT ─────────────────────────────────────────────────────────

@router.patch("/documents/{doc_id}/rename")
def rename_document(
    doc_id: str,
    fileName: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(
        Document.id == doc_id, Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.file_name = fileName
    db.commit()
    return {"message": "Renamed successfully", "fileName": fileName}


# ─── ASK QUESTION ────────────────────────────────────────────────────────────

@router.post("/ask")
async def ask_question(
    doc_ids: str = Form(...),
    question: str = Form(...),
    history: str = Form(default="[]"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    id_list = [d.strip() for d in doc_ids.split(",") if d.strip()]
    try:
        history_list = json.loads(history)
    except Exception:
        history_list = []

    # Check response cache first
    cached = get_cached_response(current_user.id, id_list, question)
    if cached:
        cached["cached"] = True
        return JSONResponse(content=cached)

    # Retrieval from Qdrant
    relevant_chunks = search_multiple_qdrant(id_list, question, current_user.id)
    reranked_chunks = rerank(question, relevant_chunks)
    result = answer_question(question, reranked_chunks, history=history_list)

    # Cache the response
    set_cached_response(current_user.id, id_list, question, result)
    result["cached"] = False
    return JSONResponse(content=result)