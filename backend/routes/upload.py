from fastapi import APIRouter, UploadFile, File, Form
from services.pdf import extract_text
from services.rag import (
    chunk_text,
    create_vector_store,
    search,
    answer_question,
    load_vector_store,
    load_chunks
)
import uuid
import json

router = APIRouter()


# -------------------------
# UPLOAD PDF
# -------------------------
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    text = extract_text(file.file)

    chunks = chunk_text(text)

    doc_id = str(uuid.uuid4())

    # Create FAISS index + save to disk
    index, chunks = create_vector_store(chunks, doc_id)

    # Save chunks to disk (IMPORTANT FIX)
    with open(f"storage/chunks/{doc_id}.json", "w") as f:
        json.dump(chunks, f)

    return {
        "message": "Uploaded successfully",
        "doc_id": doc_id
    }


# -------------------------
# ASK QUESTION
# -------------------------
from fastapi.responses import StreamingResponse
import time
import json

@router.post("/ask")
async def ask_question(doc_id: str = Form(...), question: str = Form(...)):

    index = load_vector_store(doc_id)
    chunks = load_chunks(doc_id)

    relevant_chunks = search(index, question, chunks)
    answer = answer_question(question, relevant_chunks)

    def stream():
        for word in answer.split():
            yield word + " "
            time.sleep(0.03)  # simulate typing effect

    return StreamingResponse(stream(), media_type="text/plain")