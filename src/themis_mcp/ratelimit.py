"""Rate limiting for THEMIS MCP tools."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("themis_mcp")


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    max_calls: int = 60
    window_seconds: int = 60


@dataclass
class RateLimitState:
    """State for a single rate limiter."""

    config: RateLimitConfig
    calls: list[float] = field(default_factory=list)

    def is_allowed(self) -> bool:
        """Check if a call is allowed under the rate limit."""
        now = time.time()
        cutoff = now - self.config.window_seconds

        # Remove old calls outside the window
        self.calls = [t for t in self.calls if t > cutoff]

        if len(self.calls) >= self.config.max_calls:
            return False

        self.calls.append(now)
        return True

    def time_until_reset(self) -> float:
        """Seconds until the oldest call expires from the window."""
        if not self.calls:
            return 0.0
        now = time.time()
        oldest = min(self.calls)
        return max(0.0, oldest + self.config.window_seconds - now)


class RateLimiter:
    """Per-tool rate limiter with configurable limits."""

    def __init__(self, default_config: RateLimitConfig | None = None):
        self._default_config = default_config or RateLimitConfig()
        self._limiters: dict[str, RateLimitState] = defaultdict(
            lambda: RateLimitState(config=self._default_config)
        )

    def configure(self, tool_name: str, config: RateLimitConfig) -> None:
        """Configure rate limits for a specific tool."""
        self._limiters[tool_name] = RateLimitState(config=config)

    def is_allowed(self, tool_name: str) -> bool:
        """Check if a call to the given tool is allowed."""
        return self._limiters[tool_name].is_allowed()

    def time_until_reset(self, tool_name: str) -> float:
        """Seconds until the rate limit resets for the given tool."""
        return self._limiters[tool_name].time_until_reset()

    def get_usage(self, tool_name: str) -> dict[str, Any]:
        """Get current usage stats for a tool."""
        state = self._limiters[tool_name]
        now = time.time()
        cutoff = now - state.config.window_seconds
        active_calls = [t for t in state.calls if t > cutoff]

        return {
            "tool": tool_name,
            "calls_in_window": len(active_calls),
            "max_calls": state.config.max_calls,
            "window_seconds": state.config.window_seconds,
            "time_until_reset": state.time_until_reset(),
        }


# Global rate limiter instance
rate_limiter = RateLimiter(
    default_config=RateLimitConfig(max_calls=60, window_seconds=60)
)

# Configure per-tool limits for expensive operations
rate_limiter.configure(
    "themis_ask",
    RateLimitConfig(max_calls=30, window_seconds=60),
)
