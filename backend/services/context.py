from typing import List, Dict, Tuple
from core.config import config


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(text) // 4


def compress_context(
    chunks: List[Dict],
    query: str,
    max_tokens: int = None,
) -> Tuple[List[Dict], int]:
    """
    Trim the chunk list so the total context stays within max_tokens.
    Chunks are already ranked by relevance — keep from the top.

    Args:
        chunks: reranked chunks (best first)
        query: used for token budget header
        max_tokens: hard cap (defaults to config)

    Returns:
        (kept_chunks, estimated_token_count)
    """
    max_tokens = max_tokens or config.MAX_CONTEXT_TOKENS
    # Reserve ~200 tokens for query + system prompt overhead
    budget = max_tokens - _estimate_tokens(query) - 200

    kept: List[Dict] = []
    used = 0

    for chunk in chunks:
        chunk_tokens = _estimate_tokens(chunk["text"])
        if used + chunk_tokens > budget:
            # Try to fit a trimmed version if nothing kept yet
            if not kept:
                trimmed_text = chunk["text"][: (budget - used) * 4]
                trimmed = {**chunk, "text": trimmed_text}
                kept.append(trimmed)
                used += _estimate_tokens(trimmed_text)
            break
        kept.append(chunk)
        used += chunk_tokens

    return kept, used


def build_context_string(chunks: List[Dict]) -> str:
    """Format chunks into a numbered context block for the LLM."""
    parts = [
        f"[{i+1}] (File: {c['fileName']}, Page {c['page']})\n{c['text']}"
        for i, c in enumerate(chunks)
    ]
    return "\n\n".join(parts)