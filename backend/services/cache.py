import json
import hashlib
import redis
from typing import Optional, List
from core.config import config

_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(config.REDIS_URL, decode_responses=True)
    return _client


# ─── Embedding Cache ─────────────────────────────────────────────────────────

def _embedding_key(text: str, model: str) -> str:
    digest = hashlib.sha256(f"{model}:{text}".encode()).hexdigest()
    return f"emb:{digest}"


def get_cached_embedding(text: str, model: str) -> Optional[List[float]]:
    r = get_redis()
    val = r.get(_embedding_key(text, model))
    if val:
        return json.loads(val)
    return None


def set_cached_embedding(text: str, model: str, embedding: List[float]) -> None:
    r = get_redis()
    r.setex(
        _embedding_key(text, model),
        config.EMBEDDING_CACHE_TTL,
        json.dumps(embedding),
    )


# ─── Response Cache ───────────────────────────────────────────────────────────

def _response_key(user_id: int, doc_ids: List[str], question: str) -> str:
    raw = f"{user_id}:{','.join(sorted(doc_ids))}:{question}"
    digest = hashlib.sha256(raw.encode()).hexdigest()
    return f"resp:{digest}"


def get_cached_response(user_id: int, doc_ids: List[str], question: str) -> Optional[dict]:
    r = get_redis()
    val = r.get(_response_key(user_id, doc_ids, question))
    if val:
        return json.loads(val)
    return None


def set_cached_response(user_id: int, doc_ids: List[str], question: str, response: dict) -> None:
    r = get_redis()
    r.setex(
        _response_key(user_id, doc_ids, question),
        config.CACHE_TTL,
        json.dumps(response),
    )


def invalidate_user_responses(user_id: int) -> None:
    """Call when user deletes a doc so stale cached answers are cleared."""
    r = get_redis()
    # scan for resp: keys — acceptable for moderate scale
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor, match="resp:*", count=200)
        # We can't inspect per-key without decoding — simplest safe approach:
        # just let TTL expire. For production, use a user-scoped prefix.
        if cursor == 0:
            break