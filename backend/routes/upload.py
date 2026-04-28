from fastapi import APIRouter, UploadFile, File
from services.pdf import extract_text
from services.llm import summarize

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    text = extract_text(file.file)
    summary = summarize(text)

    return {
        "summary": summary
    }