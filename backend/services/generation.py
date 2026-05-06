from typing import List, Dict, Optional
from openai import OpenAI

from core.config import config


def _get_client() -> OpenAI:
    return OpenAI(api_key=config.OPENAI_API_KEY)


def answer_question(
    query: str,
    context_chunks: List[Dict],
    history: Optional[List[Dict]] = None,
    client: OpenAI = None,
) -> Dict:
    """
    Generate an answer with inline citations from retrieved chunks.

    Args:
        query: user's question
        context_chunks: list of {"text", "page", "doc_id", "fileName"}
        history: prior conversation turns [{"role", "content"}, ...]
        client: optional OpenAI client for DI

    Returns:
        {"answer": str, "citations": [{"page", "fileName", "snippet"}]}
    """
    client = client or _get_client()

    # Build numbered context block
    context_parts = [
        f"[{i+1}] (File: {chunk['fileName']}, Page {chunk['page']})\n{chunk['text']}"
        for i, chunk in enumerate(context_chunks)
    ]
    context = "\n\n".join(context_parts)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a document assistant. Answer using ONLY the provided document context. "
                "When you use information from a source, cite it inline using [1], [2], etc. "
                "matching the numbers in the context. Be concise and accurate. "
                "You have access to the conversation history to answer follow-up questions."
            ),
        }
    ]

    if history:
        for turn in history[-(config.MAX_HISTORY_TURNS):]:
            messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append(
        {
            "role": "user",
            "content": f"Document context:\n{context}\n\nQuestion: {query}",
        }
    )

    response = client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=messages,
    )
    answer = response.choices[0].message.content

    # Deduplicated citations preserving order
    seen: set = set()
    citations: List[Dict] = []
    for chunk in context_chunks:
        key = (chunk["doc_id"], chunk["page"])
        if key not in seen:
            seen.add(key)
            citations.append(
                {
                    "page": chunk["page"],
                    "fileName": chunk["fileName"],
                    "snippet": chunk["text"][:200].strip(),
                }
            )

    return {"answer": answer, "citations": citations}