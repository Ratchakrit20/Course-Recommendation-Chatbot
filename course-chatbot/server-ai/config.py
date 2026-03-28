import os
from typing import List

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CHROMA_ROOT = os.getenv("CHROMA_ROOT", os.path.join(BASE_DIR, "chroma_db2"))


def _get_env_str(name: str, default: str) -> str:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else default


def _get_env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _get_env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _get_env_list(name: str, default: str) -> List[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


OLLAMA_BASE_URL = _get_env_str("OLLAMA_BASE_URL", "http://host.docker.internal:11434").rstrip("/")
OLLAMA_MODEL = _get_env_str("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_EMBED_MODEL = _get_env_str("OLLAMA_EMBED_MODEL", "nomic-embed-text-v2-moe")

DEFAULT_TOP_K = _get_env_int("DEFAULT_TOP_K", 10)
DEFAULT_PROVIDER = _get_env_str("DEFAULT_PROVIDER", "ollama").lower()

OLLAMA_KEEP_ALIVE = _get_env_str("OLLAMA_KEEP_ALIVE", "10m")
OLLAMA_TEMPERATURE = _get_env_float("OLLAMA_TEMPERATURE", 0.0)
OLLAMA_NUM_PREDICT = _get_env_int("OLLAMA_NUM_PREDICT", 700)

OLLAMA_CONNECT_TIMEOUT = _get_env_float("OLLAMA_CONNECT_TIMEOUT", 5.0)
OLLAMA_READ_TIMEOUT = _get_env_float("OLLAMA_READ_TIMEOUT", 120.0)

CORS_ORIGINS = _get_env_list(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
)