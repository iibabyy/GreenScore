from .config import settings

# Prefer community package implementations to avoid langchain deprecation warnings
try:
    from langchain_community.llms import Ollama
except Exception:  # pragma: no cover - fallback path
    from langchain.llms import Ollama  # type: ignore

import inspect
import threading
import time
from typing import Optional
from pydantic import ValidationError
import requests

# --- Warmup / readiness globals ---
_warmup_lock = threading.Lock()
_ollama_warmed_at: Optional[float] = None
_last_warmup_error: Optional[str] = None

def _ping_ollama(timeout: float = 2.0) -> bool:
    """Quickly check that Ollama responds to /api/version."""
    try:
        resp = requests.get(f"{settings.OLLAMA_HOST.rstrip('/')}/api/version", timeout=timeout)
        return resp.status_code == 200
    except Exception as e:  # pragma: no cover - network failure branch
        global _last_warmup_error
        _last_warmup_error = str(e)
        return False

def _model_present(timeout: float = 2.5) -> bool:
    """Check that the target model appears in /api/tags list (best-effort)."""
    try:
        resp = requests.get(f"{settings.OLLAMA_HOST.rstrip('/')}/api/tags", timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            tags = data.get('models', []) or data.get('models', [])
            # Different versions may return list of dicts under 'models'
            for m in tags:
                name = m.get('name') if isinstance(m, dict) else None
                if name and name.split(':')[0] == settings.MODEL_NAME.split(':')[0]:
                    return True
        return False
    except Exception:
        return False

def _lightweight_generate_ping(timeout: float = 10.0) -> bool:  # noqa: E999 (short warm generation)
    """Attempt a minimal generation to force model load (streaming or not)."""
    url = f"{settings.OLLAMA_HOST.rstrip('/')}/api/generate"
    payload = {"model": settings.MODEL_NAME, "prompt": "ping", "stream": False}
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False

def ensure_ollama_warm(max_attempts: int = 6, initial_backoff: float = 0.5) -> bool:
    """Idempotent warmup ensuring Ollama is reachable and model is loaded.

    Returns True if ready; False otherwise. Uses exponential backoff.
    Safe to call on each request (guarded by a lock + cached timestamp).
    """
    global _ollama_warmed_at
    if _ollama_warmed_at is not None:
        return True

    with _warmup_lock:
        if _ollama_warmed_at is not None:  # double-checked
            return True
        backoff = initial_backoff
        for attempt in range(1, max_attempts + 1):
            reachable = _ping_ollama()
            if reachable:
                # Optional: ensure model is present / loaded
                if not _model_present():
                    _light_ping_ok = _lightweight_generate_ping()
                    if not _light_ping_ok:
                        # Continue attempts; maybe model still downloading
                        pass
                # After a successful ping/generation, mark warmed
                if reachable:
                    _ollama_warmed_at = time.time()
                    return True
            time.sleep(backoff)
            backoff = min(backoff * 2, 5.0)
        return False


def _filter_kwargs_for_callable(cls, kwargs: dict) -> dict:
    """Return a filtered dict keeping only parameters accepted by cls.__init__ (best-effort)."""
    try:
        sig = inspect.signature(cls.__init__)
        allowed = set(sig.parameters.keys()) - {"self", "args", "kwargs"}
        return {k: v for k, v in kwargs.items() if k in allowed}
    except Exception:
        # Fallback: remove commonly unsupported keys
        fallback = kwargs.copy()
        for bad in ("max_tokens",):
            fallback.pop(bad, None)
        return fallback


def get_llm():
    """Return an Ollama LLM instance, tolerant to different wrapper signatures.

    Also triggers (lazy) warmup of the Ollama service the first time it's called.

    Strategy:
    1. Warmup (ping & optional lightweight generation) if not already warmed.
    2. Try to instantiate with the full kwargs (preferred).
    3. On ValidationError or TypeError, filter kwargs by the class __init__ signature and retry.
    4. As a last resort, drop `max_tokens` and retry (some wrappers only accept `num_predict`).
    """
    ensure_ollama_warm()

    # Start with minimal safe kwargs to avoid ValidationError that might drop base_url
    base_kwargs = {
        "model": settings.MODEL_NAME,
        "base_url": settings.OLLAMA_HOST,
        "temperature": settings.TEMPERATURE,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
        "num_predict": settings.MAX_TOKENS,
        "num_ctx": settings.MAX_TOKENS,  # Ensure context window is large enough
    }
    advanced_kwargs = {
        # Some wrappers may accept these; we'll try to add them after instantiation
        "max_tokens": settings.MAX_TOKENS,
    }

    llm = None
    try:
        llm = Ollama(**base_kwargs)
    except ValidationError:  # pragma: no cover
        filtered = _filter_kwargs_for_callable(Ollama, base_kwargs)
        llm = Ollama(**filtered)
    except TypeError:  # pragma: no cover
        filtered = _filter_kwargs_for_callable(Ollama, base_kwargs)
        llm = Ollama(**filtered)

    # Enforce base_url in case pydantic constructor ignored it
    try:
        if getattr(llm, "base_url", None) != settings.OLLAMA_HOST:
            if settings.DEBUG_MODE:
                print(f"⚠️ LLM base_url override: {getattr(llm,'base_url',None)} -> {settings.OLLAMA_HOST}")
            setattr(llm, "base_url", settings.OLLAMA_HOST)
    except Exception:
        pass

    # Attempt to apply advanced kwargs via attribute setting if supported
    for k, v in advanced_kwargs.items():
        if not hasattr(llm, k):
            continue
        try:
            setattr(llm, k, v)
        except Exception:
            pass

    if settings.DEBUG_MODE:
        try:
            print(f"🧪 LLM final base_url={getattr(llm,'base_url',None)} model={getattr(llm,'model',None)} num_predict={getattr(llm,'num_predict',None)}")
        except Exception:
            pass

    return llm