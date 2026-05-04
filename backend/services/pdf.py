from pypdf import PdfReader
import io

def extract_text(file):
    """Returns list of {page: int, text: str} — one entry per PDF page."""
    try:
        file_bytes = file.read()
        pdf_stream = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_stream)

        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"page": i + 1, "text": text})

        return pages

    except Exception as e:
        return [{"page": 1, "text": f"Error reading PDF: {str(e)}"}]