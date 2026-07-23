"""MCP tools: ask (LLM Q&A) and lookup (anchor table retrieval)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from themis_mcp.resources import DISCLAIMER

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
    grounded: bool,
    section: str | None,
    act: str | None,
    confidence: float | None,
    warning: str | None,
) -> str:
    """Format a model response with metadata and disclaimer."""
    parts = [text]

    meta = []
    if section:
        meta.append(f"Section: {section}")
    if act:
        meta.append(f"Act: {act}")
    if confidence is not None:
        meta.append(f"Confidence: {confidence:.2f}")
    if grounded:
        meta.append("Grounded: Yes")
    else:
        meta.append("Grounded: No")
    if warning:
        meta.append(f"Warning: {warning}")

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
) -> str:
    """Ask a legal question about Indian statutory law.

    Uses the THEMIS retrieval-grounded model. The response includes the answer,
    section/act metadata, grounding status, and a legal disclaimer.

    Args:
        question: A legal question about Indian statutory law (BNS, IPC, BNSS, BSA, RTI, etc.)
        temperature: Generation temperature (0.0-1.0). Lower = more deterministic.
        max_tokens: Maximum tokens to generate.

    Returns:
        Formatted response with answer, metadata, and disclaimer.
    """
    if _model is None:
        return (
            "Error: THEMIS model not loaded. The server may still be starting up.\n\n"
            "---\n" + DISCLAIMER
        )

    try:
        response = _model.ask(
            question,
            temperature=temperature,
            max_new_tokens=max_tokens,
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "memory" in error_msg or "oom" in error_msg:
            help_msg = (
                "Insufficient GPU memory for inference. "
                "Try reducing max_tokens or close other GPU applications.\n"
                f"Details: {e}"
            )
        else:
            help_msg = f"Inference failed: {e}"

        return f"Error: {help_msg}\n\n---\n" + DISCLAIMER

    return _format_response(
        text=response.text,
        grounded=response.grounded,
        section=getattr(response, "section", None),
        act=getattr(response, "act", None),
        confidence=getattr(response, "confidence", None),
        warning=getattr(response, "warning", None),
    )


def _load_anchor_table(act: str) -> dict[str, str]:
    """Load an anchor table CSV from the themis package data.

    Returns a dict mapping section number -> section text.
    """
    try:
        themis_pkg = importlib.import_module("themis")
        pkg_dir = Path(themis_pkg.__file__).parent
    except (ImportError, AttributeError) as err:
        raise RuntimeError(
            "Cannot locate the themis package. Install it with: pip install themis-llm"
        ) from err

    anchor_path = pkg_dir / "data" / "anchors" / f"{act}.csv"
    if not anchor_path.exists():
        raise FileNotFoundError(
            f"Anchor table not found for act '{act}'. Expected: {anchor_path}"
        )

    table: dict[str, str] = {}
    with open(anchor_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            section_num = row.get("section") or row.get("section_number") or ""
            text = row.get("text") or row.get("section_text") or ""
            if section_num:
                table[section_num.strip()] = text.strip()

    return table


def lookup(act: str, section: str) -> str:
    """Look up the raw text of a specific legal section from anchor tables.

    This performs direct retrieval without LLM inference — fast and deterministic.

    Args:
        act: Act identifier. One of: bns, bnss, bsa, ipc, rti_2005, consumer_protection_2019
        section: Section number (e.g. "302", "Section 63")

    Returns:
        Raw section text with disclaimer.
    """
    section_clean = section.replace("Section ", "").replace("section ", "").strip()

    try:
        table = _load_anchor_table(act)
    except (RuntimeError, FileNotFoundError) as e:
        return f"Error: {e}\n\n---\n{DISCLAIMER}"

    text = table.get(section_clean)

    if not text:
        available = sorted(table.keys(), key=lambda x: int(x) if x.isdigit() else 0)
        return (
            f"Section {section_clean} not found in '{act}'. "
            f"Available sections: {', '.join(available[:20])}"
            f"{'...' if len(available) > 20 else ''}\n\n---\n{DISCLAIMER}"
        )

    header = f"Section {section_clean} — {act.upper()}"
    return f"{header}\n\n{text}\n\n---\n{DISCLAIMER}"
