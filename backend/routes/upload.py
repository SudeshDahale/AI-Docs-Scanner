from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from services.pdf import extract_text
from services.rag import (
    chunk_text,
    create_vector_store,
    search_multiple,
    answer_question,
    load_chunks
)
import uuid
import json
import time

router = APIRouter()


# -------------------------
# UPLOAD PDF (unchanged)
# -------------------------
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    text = extract_text(file.file)
    chunks = chunk_text(text)
    doc_id = str(uuid.uuid4())

    index, chunks = create_vector_store(chunks, doc_id)

    with open(f"storage/chunks/{doc_id}.json", "w") as f:
        json.dump(chunks, f)

    return {
        "message": "Uploaded successfully",
        "doc_id": doc_id
    }


# -------------------------
# ASK QUESTION (now multi-doc)
# -------------------------
@router.post("/ask")
async def ask_question(doc_ids: str = Form(...), question: str = Form(...)):
    # doc_ids is a comma-separated string: "id1,id2,id3"
    id_list = [d.strip() for d in doc_ids.split(",") if d.strip()]

    relevant_chunks = search_multiple(id_list, question)
    answer = answer_question(question, relevant_chunks)

    def stream():
        for word in answer.split():
            yield word + " "
            time.sleep(0.03)

    return StreamingResponse(stream(), media_type="text/plain")