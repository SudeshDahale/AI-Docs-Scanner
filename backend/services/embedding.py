import time
import numpy as np
from typing import List, Optional
from openai import OpenAI
from core.config import config
from services.cache import get_cached_embedding, set_cached_embedding


def _get_client() -> OpenAI:
    return OpenAI(api_key=config.OPENAI_API_KEY)


def get_embedding(text: str, client: OpenAI = None) -> List[float]:
    """Embed a single string, with Redis cache."""
    cached = get_cached_embedding(text, config.EMBEDDING_MODEL)
    if cached:
        return cached

    client = client or _get_client()
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=text,
    )
    embedding = response.data[0].embedding
    set_cached_embedding(text, config.EMBEDDING_MODEL, embedding)
    return embedding


def get_embeddings_batch(
    texts: List[str],
    client: Optional[OpenAI] = None,
    batch_size: int = 100,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> List[List[float]]:
    """Embed a list of texts. Hits Redis cache per-text before calling API."""
    client = client or _get_client()
    all_embeddings: List[Optional[List[float]]] = [None] * len(texts)

    # Separate cached vs uncached
    uncached_indices = []
    for i, text in enumerate(texts):
        cached = get_cached_embedding(text, config.EMBEDDING_MODEL)
        if cached:
            all_embeddings[i] = cached
        else:
            uncached_indices.append(i)

    if not uncached_indices:
        return all_embeddings  # type: ignore

    uncached_texts = [texts[i] for i in uncached_indices]

    fetched: List[List[float]] = []
    for start in range(0, len(uncached_texts), batch_size):
        batch = uncached_texts[start: start + batch_size]
        last_error = None
        for attempt in range(max_retries):
            try:
                response = client.embeddings.create(
                    model=config.EMBEDDING_MODEL,
                    input=batch,
                )
                batch_embeddings = [
                    item.embedding
                    for item in sorted(response.data, key=lambda x: x.index)
                ]
                fetched.extend(batch_embeddings)
                break
            except Exception as e:
                last_error = e
                time.sleep(retry_delay * (2 ** attempt))
        else:
            raise RuntimeError(
                f"Embedding batch failed after {max_retries} retries: {last_error}"
            )

    # Fill in results + populate cache
    for idx, orig_i in enumerate(uncached_indices):
        emb = fetched[idx]
        all_embeddings[orig_i] = emb
        set_cached_embedding(texts[orig_i], config.EMBEDDING_MODEL, emb)

    return all_embeddings  # type: ignore