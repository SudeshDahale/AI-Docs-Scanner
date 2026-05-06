import os
from dotenv import load_dotenv

load_dotenv()


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

    # Storage
    STORAGE_BASE: str = os.getenv("STORAGE_BASE", "storage")

    # Sprint 2
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    BM25_WEIGHT: float = float(os.getenv("BM25_WEIGHT", "0.3"))
    FAISS_WEIGHT: float = float(os.getenv("FAISS_WEIGHT", "0.7"))
    MAX_CONTEXT_TOKENS: int = int(os.getenv("MAX_CONTEXT_TOKENS", "2000"))
    RERANK_TOP_N: int = int(os.getenv("RERANK_TOP_N", "5"))

    @property
    def index_dir(self) -> str:
        return os.path.join(self.STORAGE_BASE, "indexes")

    @property
    def chunk_dir(self) -> str:
        return os.path.join(self.STORAGE_BASE, "chunks")


config = Config()