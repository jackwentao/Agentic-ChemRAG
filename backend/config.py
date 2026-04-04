from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return float(value)


def _resolve_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default

    path = Path(value).expanduser()
    if not path.is_absolute():
        path = ROOT_DIR / path
    return path.resolve()


def _split_csv(value: str) -> list[str]:
    if value.strip() == "*":
        return ["*"]
    return [item.strip() for item in value.split(",") if item.strip()]


DATA_DIR = _resolve_path("DATA_DIR", ROOT_DIR / "data")
PDF_DIR = _resolve_path("PDF_DIR", DATA_DIR / "pdf")
IMAGE_DIR = _resolve_path("IMAGE_DIR", DATA_DIR / "extracted_images")
CHROMA_DIR = _resolve_path("CHROMA_DIR", DATA_DIR / "chroma_db")

BACKEND_HOST = _env("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = _env_int("BACKEND_PORT", 8000)
FRONTEND_PORT = _env_int("FRONTEND_PORT", 5173)
BACKEND_ORIGIN = _env("BACKEND_ORIGIN", f"http://localhost:{BACKEND_PORT}")

VITE_API_BASE_URL = _env("VITE_API_BASE_URL", "")
VITE_DATA_BASE_URL = _env("VITE_DATA_BASE_URL", "")

EMBEDDING_MODEL = _env("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
RERANKER_MODEL = _env("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
REWRITE_MODEL = _env("REWRITE_MODEL", "deepseek-chat")
ANSWER_MODEL = _env("ANSWER_MODEL", "deepseek-chat")

RETRIEVAL_K = _env_int("RETRIEVAL_K", 10)
RETRIEVAL_SCORE_THRESHOLD = _env_float("RETRIEVAL_SCORE_THRESHOLD", 0.5)
RERANK_TOP_N = _env_int("RERANK_TOP_N", 3)
SESSION_MAX_ROUNDS = _env_int("SESSION_MAX_ROUNDS", 3)

CORS_ALLOW_ORIGINS = _split_csv(
    _env("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
)