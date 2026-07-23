"""THEMIS MCP Server — Indian statutory law Q&A via retrieval-grounded LLM."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP

from themis_mcp.resources import get_acts, get_disclaimer
from themis_mcp.tools import ask, lookup

logger = logging.getLogger("themis_mcp")


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Load the THEMIS model once at server startup."""
    logger.info("Loading THEMIS model...")
    from themis.model import ThemisModel

    model = ThemisModel.from_pretrained()
    logger.info("THEMIS model loaded successfully.")
    yield {"model": model}

mcp = FastMCP(
    "themis-mcp",
    instructions=(
        "THEMIS MCP provides Indian statutory law Q&A and section lookup. "
        "Use the 'ask' tool for legal questions about BNS, IPC, BNSS, BSA, RTI, "
        "and other Indian statutes. Use the 'lookup' tool to retrieve raw section "
        "text directly from anchor tables without LLM inference."
    ),
    lifespan=lifespan,
)


@mcp.tool()
def themis_ask(
    question: str,
    temperature: float = 0.7,
    max_tokens: int = 512,
) -> str:
    """Ask a legal question about Indian statutory law.

    Uses the THEMIS retrieval-grounded model to answer questions about:
    - Bharatiya Nyaya Sanhita (BNS) 2023
    - Indian Penal Code (IPC) 1860
    - Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023
    - Bharatiya Sakshya Adhiniyam (BSA) 2023
    - Right to Information Act (RTI) 2005
    - Consumer Protection Act (CPA) 2019
    - Constitution of India

    The response includes section/act metadata and grounding status.
    All responses include a legal disclaimer.
    """
    return ask(question, temperature=temperature, max_tokens=max_tokens)


@mcp.tool()
def themis_lookup(act: str, section: str) -> str:
    """Look up the raw text of a specific legal section from anchor tables.

    This performs direct retrieval without LLM inference — fast and deterministic.
    Use this when you need the exact statutory text rather than an interpretation.

    Args:
        act: Act identifier. One of: bns, bnss, bsa, ipc, rti_2005, consumer_protection_2019
        section: Section number (e.g. "302", "63", "Section 1")

    Returns:
        The raw section text with a legal disclaimer.
    """
    return lookup(act=act, section=section)


@mcp.resource("themis://disclaimer")
def resource_disclaimer() -> str:
    """Legal disclaimer for THEMIS MCP responses."""
    return get_disclaimer()


@mcp.resource("themis://acts")
def resource_acts() -> str:
    """List of supported Indian statutes and their section counts."""
    return get_acts()


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
