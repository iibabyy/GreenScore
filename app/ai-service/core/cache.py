import time
import hashlib
import threading
from typing import Any, Dict, Optional

class LRUCacheEntry:
    __slots__ = ("value", "ts")
    def __init__(self, value: Any):
        self.value = value
        self.ts = time.time()

class LRUCache:
    def __init__(self, max_size: int = 128, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._data: Dict[str, LRUCacheEntry] = {}
        self._lock = threading.Lock()

    def _evict_if_needed(self):
        if len(self._data) <= self.max_size:
            return
        # Evict oldest
        oldest_key = min(self._data.items(), key=lambda kv: kv[1].ts)[0]
        self._data.pop(oldest_key, None)

    def _expired(self, entry: LRUCacheEntry) -> bool:
        return (time.time() - entry.ts) > self.ttl

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            if self._expired(entry):
                self._data.pop(key, None)
                return None
            # touch
            entry.ts = time.time()
            return entry.value

    def set(self, key: str, value: Any):
        with self._lock:
            self._data[key] = LRUCacheEntry(value)
            self._evict_if_needed()

_global_cache = LRUCache(max_size=200, ttl_seconds=600)


def _hash_key(prefix: str, *parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode('utf-8'))
    return prefix + ':' + h.hexdigest()[:24]


def cached_answer(question: str, prompt_version: str, generator_fn):
    key = _hash_key('ask', question.strip(), prompt_version)
    cached = _global_cache.get(key)
    if cached is not None:
        return cached, True
    value = generator_fn()
    _global_cache.set(key, value)
    return value, False
