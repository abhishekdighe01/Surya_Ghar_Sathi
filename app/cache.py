# ==============================================================================
# File: app/cache.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 13 - High-Performance Thread-Safe TTL Query Cache.
#              Caches frequent semantic and RAG query responses with sub-millisecond
#              retrieval times to reduce LLM token usage and latency.
# ==============================================================================

import hashlib
import json
import logging
import re
import threading
import time
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cache")


class QueryCache:
    """
    Thread-safe in-memory cache with Time-To-Live (TTL) expiration.
    Normalizes query strings to prevent cache misses caused by trivial whitespace,
    casing, or punctuation differences.
    """

    def __init__(self, default_ttl_seconds: int = 3600):
        self._cache: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.default_ttl = default_ttl_seconds
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    @staticmethod
    def normalize_query(query: str) -> str:
        """
        Normalize query string: lowercase, collapse whitespace, strip punctuation.
        """
        cleaned = query.lower().strip()
        cleaned = re.sub(r"[^\w\s]", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned

    def compute_key(self, query: str, **kwargs) -> str:
        """
        Generate a deterministic MD5 hash key from normalized query and additional kwargs.
        """
        normalized_q = self.normalize_query(query)
        payload = {"q": normalized_q}
        if kwargs:
            for k in sorted(kwargs.keys()):
                payload[k] = kwargs[k]
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.md5(serialized.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Any | None:
        """
        Retrieve value from cache if present and unexpired.
        """
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                self.misses += 1
                return None

            now = time.time()
            if now > entry["expires_at"]:
                # Expired: evict entry
                del self._cache[key]
                self.evictions += 1
                self.misses += 1
                return None

            self.hits += 1
            return entry["value"]

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Store a value in the cache with expiration timestamp.
        """
        ttl_val = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + ttl_val
        with self._lock:
            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time(),
            }

    def clear(self) -> None:
        """Flush the entire cache and reset counters."""
        with self._lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0
            self.evictions = 0
        logger.info("QueryCache cleared successfully.")

    def get_stats(self) -> dict[str, Any]:
        """Return cache health and usage statistics."""
        with self._lock:
            active_entries = len(self._cache)
            total_requests = self.hits + self.misses
            hit_ratio = round(self.hits / total_requests, 4) if total_requests > 0 else 0.0
            return {
                "active_entries": active_entries,
                "hits": self.hits,
                "misses": self.misses,
                "total_requests": total_requests,
                "hit_ratio": hit_ratio,
                "evictions": self.evictions,
                "default_ttl_seconds": self.default_ttl,
            }


# Singleton instance for system-wide access
query_cache = QueryCache(default_ttl_seconds=3600)
