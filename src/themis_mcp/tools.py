"""MCP tools: ask (LLM Q&A) and lookup (anchor table retrieval)."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from themis_mcp.cache import cache
from themis_mcp.errors import classify_error
from themis_mcp.metrics import metrics
from themis_mcp.ratelimit import rate_limiter
from themis_mcp.resources import DISCLAIMER
from themis_mcp.structured import LookupResult, ToolResult
from themis_mcp.tracing import trace_tool

if TYPE_CHECKING:
    pass

logger = logging.getLogger("themis_mcp")

_model: Any = None
_section_index: Any = None


def set_model(model: Any) -> None:
    """Store the loaded THEMIS model for tool use."""
    global _model
    _model = model
    logger.info("Model stored for MCP tools.")


def _format_response(
    text: str,
    section: str | None = None,
    act: str | None = None,
) -> str:
    """Format a model response with disclaimer."""
    parts = [text]

    meta = []
    if section:
        meta.append(f"Section: {section}")
    if act:
        meta.append(f"Act: {act}")

    if meta:
        parts.append("")
        parts.append("---")
        parts.extend(meta)

    parts.append("")
    parts.append("---")
    parts.append(DISCLAIMER)

    return "\n".join(parts)


def ask(
    question: str,
    temperature: float = 0.7,
    max_tokens: int = 512,
) -> ToolResult:
    """Ask a legal question about Indian statutory law.

    Uses the THEMIS retrieval-grounded model. The response includes the answer,
    section/act metadata, grounding status, and a legal disclaimer.

    Args:
        question: A legal question about Indian statutory law (BNS, IPC, BNSS, BSA, RTI, etc.)
        temperature: Generation temperature (0.0-1.0). Lower = more deterministic.
        max_tokens: Maximum tokens to generate.

    Returns:
        ToolResult with text and structured metadata.
    """
    metrics.inc_counter("themis_tool_calls_total", {"tool": "themis_ask"})
    start = time.monotonic()

    if _model is None:
        metrics.inc_counter(
            "themis_tool_errors_total",
            {"tool": "themis_ask", "error": "model_not_loaded"},
        )
        return ToolResult(
            text="THEMIS model not loaded. The server may still be starting up.",
            error=True,
            error_class="SERVER_ERROR",
        )

    if not rate_limiter.is_allowed("themis_ask"):
        reset_time = rate_limiter.time_until_reset("themis_ask")
        metrics.inc_counter(
            "themis_tool_errors_total", {"tool": "themis_ask", "error": "rate_limited"}
        )
        return ToolResult(
            text=f"Rate limit exceeded. Try again in {reset_time:.0f} seconds.",
            error=True,
            error_class="RATE_LIMITED",
        )

    # Check cache (only for deterministic queries: temperature <= 0.1)
    if temperature <= 0.1:
        cached = cache.get(
            "themis_ask",
            question=question,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if cached is not None:
            logger.info(f"Cache hit for question: {question[:50]}...")
            metrics.inc_counter("themis_cache_hits_total", {"tool": "themis_ask"})
            metrics.observe_histogram(
                "themis_tool_duration_seconds",
                time.monotonic() - start,
                {"tool": "themis_ask"},
            )
            return cached  # type: ignore[no-any-return]

    with trace_tool("themis_ask", question=question[:100]):
        try:
            response = _model.generate(
                question,
                temperature=temperature,
                max_new_tokens=max_tokens,
            )
        except Exception as e:
            error = classify_error(e)
            metrics.inc_counter(
                "themis_tool_errors_total",
                {"tool": "themis_ask", "error": error.error_class.value},
            )
            metrics.observe_histogram(
                "themis_tool_duration_seconds",
                time.monotonic() - start,
                {"tool": "themis_ask"},
            )
            return ToolResult(
                text=error.message,
                error=True,
                error_class=error.error_class.value,
            )

    result = ToolResult(
        text=response.response,
    )

    metrics.observe_histogram(
        "themis_tool_duration_seconds", time.monotonic() - start, {"tool": "themis_ask"}
    )

    # Cache result (only for deterministic queries)
    if temperature <= 0.1:
        cache.set(
            "themis_ask",
            result,
            question=question,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    return result


def _get_section_index() -> Any:
    """Get or initialize the SectionIndex from themis.grounding."""
    global _section_index
    if _section_index is None:
        try:
            from themis.grounding import SectionIndex

            _section_index = SectionIndex()
        except (ImportError, ModuleNotFoundError) as err:
            raise RuntimeError(
                "SectionIndex not available in this version of themis-llm. "
                "The lookup tool requires themis-llm with grounding support."
            ) from err
    return _section_index


def lookup(act: str, section: str) -> LookupResult:
    """Look up the raw text of a specific legal section from anchor tables.

    This performs direct retrieval without LLM inference — fast and deterministic.

    Args:
        act: Act identifier. One of: bns, bnss, bsa, ipc, rti_2005, consumer_protection_2019
        section: Section number (e.g. "302", "Section 63")

    Returns:
        LookupResult with structured section data.
    """
    metrics.inc_counter("themis_tool_calls_total", {"tool": "themis_lookup"})
    start = time.monotonic()
    section_clean = section.replace("Section ", "").replace("section ", "").strip()

    with trace_tool("themis_lookup", act=act, section=section_clean):
        try:
            index = _get_section_index()
        except RuntimeError as e:
            metrics.inc_counter(
                "themis_tool_errors_total",
                {"tool": "themis_lookup", "error": "import_error"},
            )
            metrics.observe_histogram(
                "themis_tool_duration_seconds",
                time.monotonic() - start,
                {"tool": "themis_lookup"},
            )
            return LookupResult(
                found=False,
                text=str(e),
            )

        try:
            result = index.lookup(section_clean, act_hint=act)
        except AttributeError:
            metrics.inc_counter(
                "themis_tool_errors_total",
                {"tool": "themis_lookup", "error": "api_mismatch"},
            )
            metrics.observe_histogram(
                "themis_tool_duration_seconds",
                time.monotonic() - start,
                {"tool": "themis_lookup"},
            )
            return LookupResult(
                found=False,
                text="SectionIndex.lookup() not available in this version of themis-llm.",
            )

    metrics.observe_histogram(
        "themis_tool_duration_seconds",
        time.monotonic() - start,
        {"tool": "themis_lookup"},
    )

    if not result.found:
        metrics.inc_counter(
            "themis_tool_errors_total", {"tool": "themis_lookup", "error": "not_found"}
        )
        return LookupResult(
            found=False,
            text=f"Section {section_clean} not found in '{act}'.",
        )

    return LookupResult(
        found=True,
        section_number=result.section_number,
        act_name=result.act_name,
        text=result.text or "No text available.",
    )
