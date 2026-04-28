from fastapi import APIRouter, UploadFile, File
from backend.services.pdf import extract_text
from backend.services.llm import summarize

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    text = extract_text(file.file)
    summary = summarize(text)

    return {
        "summary": summary
    }