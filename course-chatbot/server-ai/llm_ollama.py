import logging
from typing import Optional, Dict, Any

import requests
from requests import Session
from requests.exceptions import ConnectionError, HTTPError, Timeout, RequestException

from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_KEEP_ALIVE,
    OLLAMA_TEMPERATURE,
    OLLAMA_NUM_PREDICT,
    OLLAMA_CONNECT_TIMEOUT,
    OLLAMA_READ_TIMEOUT,
)

logger = logging.getLogger(__name__)
_session: Session = requests.Session()


class OllamaError(Exception):
    pass


class OllamaConnectionError(OllamaError):
    pass


class OllamaTimeoutError(OllamaError):
    pass


class OllamaResponseError(OllamaError):
    pass


def chat_with_ollama(
    system_prompt: str,
    user_prompt: str,
    *,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    if not user_prompt or not user_prompt.strip():
        raise ValueError("user_prompt must not be empty")

    url = f"{OLLAMA_BASE_URL}/api/chat"

    payload = {
        "model": model or OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ],
        "stream": False,
        "keep_alive": OLLAMA_KEEP_ALIVE,
        "options": {
            "temperature": OLLAMA_TEMPERATURE,
            "num_predict": OLLAMA_NUM_PREDICT,
        },
    }

    try:
        response = _session.post(
            url,
            json=payload,
            timeout=(OLLAMA_CONNECT_TIMEOUT, OLLAMA_READ_TIMEOUT),
        )
        response.raise_for_status()
        data = response.json()

        message = data.get("message", {})
        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            raise OllamaResponseError("Ollama returned an empty or invalid response")

        return {
            "content": content.strip(),
            "model": data.get("model", model or OLLAMA_MODEL),
            "done": data.get("done", True),
            "total_duration": data.get("total_duration"),
            "load_duration": data.get("load_duration"),
            "prompt_eval_count": data.get("prompt_eval_count"),
            "eval_count": data.get("eval_count"),
        }

    except Timeout as exc:
        logger.exception("Ollama request timed out")
        raise OllamaTimeoutError("Ollama request timed out") from exc
    except ConnectionError as exc:
        logger.exception("Failed to connect to Ollama")
        raise OllamaConnectionError("Failed to connect to Ollama") from exc
    except HTTPError as exc:
        logger.exception("Ollama HTTP error")
        raise OllamaResponseError(f"Ollama HTTP error: {exc}") from exc
    except RequestException as exc:
        logger.exception("Unexpected requests error")
        raise OllamaResponseError(f"Ollama request failed: {exc}") from exc
    except ValueError as exc:
        logger.exception("Invalid JSON response from Ollama")
        raise OllamaResponseError("Invalid JSON response from Ollama") from exc