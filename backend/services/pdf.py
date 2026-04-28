from pypdf import PdfReader
import io

def extract_text(file):
    try:
        file_bytes = file.read()
        pdf_stream = io.BytesIO(file_bytes)

        reader = PdfReader(pdf_stream)

        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    except Exception as e:
        return f"Error reading PDF: {str(e)}"