import time
import numpy as np
from typing import List
from openai import OpenAI
from core.config import config


def _get_client() -> OpenAI:
    return OpenAI(api_key=config.OPENAI_API_KEY)


def get_embedding(text: str, client: OpenAI = None) -> List[float]:
    """Embed a single string."""
    client = client or _get_client()
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def get_embeddings_batch(
    texts: List[str],
    client: OpenAI = None,
    batch_size: int = 100,
    max_retries: int = 3,
    retry_delay: float = 1.0,
) -> List[List[float]]:
    """
    Embed a list of texts using batched API calls with retry logic.

    Args:
        texts: list of strings to embed
        client: optional pre-built OpenAI client (for DI / testing)
        batch_size: how many texts per API call (OpenAI max is 2048)
        max_retries: attempts per batch before raising
        retry_delay: base seconds to wait between retries (exponential backoff)

    Returns:
        list of embedding vectors in the same order as `texts`
    """
    client = client or _get_client()
    all_embeddings: List[List[float]] = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        last_error = None

        for attempt in range(max_retries):
            try:
                response = client.embeddings.create(
                    model=config.EMBEDDING_MODEL,
                    input=batch,
                )
                # OpenAI returns embeddings in the same order as input
                batch_embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
                all_embeddings.extend(batch_embeddings)
                break
            except Exception as e:
                last_error = e
                wait = retry_delay * (2 ** attempt)
                time.sleep(wait)
        else:
            raise RuntimeError(
                f"Embedding batch {start}–{start+len(batch)} failed after "
                f"{max_retries} retries: {last_error}"
            )

    return all_embeddings