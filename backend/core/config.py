import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Models
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gpt-4.1-mini")

    # RAG
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "3"))
    MAX_HISTORY_TURNS: int = int(os.getenv("MAX_HISTORY_TURNS", "10"))

    # Storage (legacy flat-file, still used as fallback)
    STORAGE_BASE: str = os.getenv("STORAGE_BASE", "storage")

    # Sprint 2
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    BM25_WEIGHT: float = float(os.getenv("BM25_WEIGHT", "0.3"))
    FAISS_WEIGHT: float = float(os.getenv("FAISS_WEIGHT", "0.7"))
    MAX_CONTEXT_TOKENS: int = int(os.getenv("MAX_CONTEXT_TOKENS", "2000"))
    RERANK_TOP_N: int = int(os.getenv("RERANK_TOP_N", "5"))

    # Sprint 4 — Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))          # 1 hour
    EMBEDDING_CACHE_TTL: int = int(os.getenv("EMBEDDING_CACHE_TTL", "86400"))  # 24 hours

    # Sprint 4 — PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://documind:documind@localhost:5432/documind"
    )

    # Sprint 4 — Qdrant
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "documind")
    VECTOR_DIM: int = int(os.getenv("VECTOR_DIM", "1536"))  # text-embedding-3-small dim

    # Sprint 4 — JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    @property
    def index_dir(self) -> str:
        return os.path.join(self.STORAGE_BASE, "indexes")

    @property
    def chunk_dir(self) -> str:
        return os.path.join(self.STORAGE_BASE, "chunks")


config = Config()