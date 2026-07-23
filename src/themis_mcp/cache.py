"""LRU cache with TTL for MCP tool responses."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("themis_mcp")


@dataclass
class CacheConfig:
    """Configuration for the response cache."""

    max_size: int = 128
    ttl_seconds: float = 300.0  # 5 minutes


@dataclass
class CacheEntry:
    """A single cached response."""

    value: Any
    created_at: float = field(default_factory=time.monotonic)

    def is_expired(self, ttl: float) -> bool:
        return (time.monotonic() - self.created_at) > ttl


class ResponseCache:
    """LRU cache with TTL expiration for tool responses."""

    def __init__(self, config: CacheConfig | None = None) -> None:
        self.config = config or CacheConfig()
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _make_key(self, tool: str, **kwargs: Any) -> str:
        """Generate a cache key from tool name and arguments."""
        raw = json.dumps({"tool": tool, **kwargs}, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, tool: str, **kwargs: Any) -> Any | None:
        """Get a cached response if available and not expired."""
        key = self._make_key(tool, **kwargs)
        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            return None

        if entry.is_expired(self.config.ttl_seconds):
            del self._cache[key]
            self._misses += 1
            return None

        self._cache.move_to_end(key)
        self._hits += 1
        logger.debug(f"Cache hit for {tool}")
        return entry.value

    def set(self, tool: str, value: Any, **kwargs: Any) -> None:
        """Store a response in the cache."""
        key = self._make_key(tool, **kwargs)

        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self.config.max_size:
            self._cache.popitem(last=False)

        self._cache[key] = CacheEntry(value=value)
        logger.debug(f"Cached response for {tool}")

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    @property
    def stats(self) -> dict[str, Any]:
        """Return cache statistics."""
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self.config.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self._hits / total:.1%}" if total > 0 else "N/A",
        }


# Global cache instance
cache = ResponseCache()
