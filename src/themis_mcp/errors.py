"""Structured error handling for THEMIS MCP tools."""

from __future__ import annotations

import json
from enum import StrEnum
from typing import Any


class ErrorClass(StrEnum):
    """Error classification for MCP tool responses."""

    CLIENT_ERROR = "CLIENT_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    EXTERNAL_ERROR = "EXTERNAL_ERROR"


class ThemisError:
    """Structured error response for MCP tools.

    Attributes:
        error_class: Classification of the error (CLIENT, SERVER, EXTERNAL)
        message: Human-readable error message
        details: Additional error details
        retry_after: Seconds to wait before retrying (for EXTERNAL_ERROR)
    """

    def __init__(
        self,
        error_class: ErrorClass,
        message: str,
        details: str | None = None,
        retry_after: int | None = None,
    ):
        self.error_class = error_class
        self.message = message
        self.details = details
        self.retry_after = retry_after

    def to_json(self) -> str:
        """Serialize error to JSON string."""
        data: dict[str, Any] = {
            "error": True,
            "error_class": self.error_class.value,
            "message": self.message,
        }
        if self.details:
            data["details"] = self.details
        if self.retry_after is not None:
            data["retry_after"] = self.retry_after
        return json.dumps(data, indent=2)

    def to_text(self) -> str:
        """Format error as human-readable text."""
        parts = [f"Error ({self.error_class.value}): {self.message}"]
        if self.details:
            parts.append(f"Details: {self.details}")
        if self.retry_after is not None:
            parts.append(f"Retry after: {self.retry_after}s")
        return "\n".join(parts)


def classify_error(error: Exception) -> ThemisError:
    """Classify an exception into a structured error response."""
    error_msg = str(error).lower()

    if "cuda" in error_msg or "gpu" in error_msg or "device" in error_msg:
        return ThemisError(
            error_class=ErrorClass.SERVER_ERROR,
            message="No GPU available or CUDA not configured",
            details="THEMIS requires a GPU with ~13GB VRAM for inference.",
        )
    elif "memory" in error_msg or "oom" in error_msg:
        return ThemisError(
            error_class=ErrorClass.SERVER_ERROR,
            message="Insufficient GPU memory",
            details="THEMIS requires ~13GB VRAM. Close other GPU applications.",
        )
    elif "download" in error_msg or "connect" in error_msg or "network" in error_msg:
        return ThemisError(
            error_class=ErrorClass.EXTERNAL_ERROR,
            message="Failed to download model weights",
            details="Check your internet connection.",
            retry_after=30,
        )
    elif "import" in error_msg or "module" in error_msg:
        return ThemisError(
            error_class=ErrorClass.SERVER_ERROR,
            message="Missing dependency",
            details="Install with: pip install themis-llm",
        )
    elif "timeout" in error_msg:
        return ThemisError(
            error_class=ErrorClass.EXTERNAL_ERROR,
            message="Request timed out",
            details="The model may be overloaded.",
            retry_after=60,
        )
    else:
        return ThemisError(
            error_class=ErrorClass.SERVER_ERROR,
            message=str(error),
        )
