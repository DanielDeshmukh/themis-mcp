"""Structured output types for MCP tool responses."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Structured tool response with text and metadata."""

    text: str
    grounded: bool
    section: str | None = None
    act: str | None = None
    confidence: float | None = None
    warning: str | None = None
    error: bool = False
    error_class: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_json(self) -> str:
        """Serialize to JSON string."""
        import json

        return json.dumps(self.to_dict(), indent=2)


@dataclass(frozen=True, slots=True)
class LookupResult:
    """Structured lookup response."""

    found: bool
    section_number: str | None = None
    act_name: str | None = None
    text: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_json(self) -> str:
        """Serialize to JSON string."""
        import json

        return json.dumps(self.to_dict(), indent=2)
