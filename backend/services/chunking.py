from typing import List, Dict
from core.config import config


def chunk_text(
    pages: List[Dict],
    doc_id: str,
    file_name: str,
    chunk_size: int = None,
) -> List[Dict]:
    """
    Split page-aware text into fixed-size chunks.

    Args:
        pages: list of {"page": int, "text": str}
        doc_id: document UUID
        file_name: original filename for metadata
        chunk_size: characters per chunk (defaults to config value)

    Returns:
        list of {"text", "page", "doc_id", "fileName"}
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    chunks = []
    for page_obj in pages:
        page_num = page_obj["page"]
        text = page_obj["text"]
        for i in range(0, len(text), chunk_size):
            chunk = text[i : i + chunk_size].strip()
            if chunk:
                chunks.append(
                    {
                        "text": chunk,
                        "page": page_num,
                        "doc_id": doc_id,
                        "fileName": file_name,
                    }
                )
    return chunks