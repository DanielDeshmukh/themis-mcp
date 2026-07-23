"""THEMIS MCP Server — Indian statutory law Q&A via retrieval-grounded LLM."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from themis_mcp.resources import get_acts, get_disclaimer
from themis_mcp.tools import ask, lookup

logger = logging.getLogger("themis_mcp")

# Dynamic tool loading: configure via environment variables
# THEMIS_MCP_TOOLS: comma-separated list of tools to enable (default: "ask,lookup")
_enabled_tools = os.environ.get("THEMIS_MCP_TOOLS", "ask,lookup").split(",")
_enabled_tools = [t.strip().lower() for t in _enabled_tools]


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Load the THEMIS model once at server startup."""
    from themis_mcp.tools import set_model
    from themis_mcp.tracing import init_tracer

    init_tracer()

    logger.info("Loading THEMIS model...")
    logger.info("This may take a few minutes on first run (downloading ~13GB).")

    try:
        from themis.model import ThemisModel

        model = ThemisModel.from_pretrained()
        set_model(model)
        logger.info("THEMIS model loaded successfully.")
        yield {"model": model}
    except ImportError as e:
        error_msg = (
            "Failed to import themis package. "
            "Install it with: pip install themis-llm\n"
            f"Details: {e}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = str(e).lower()
        if "cuda" in error_msg or "gpu" in error_msg or "device" in error_msg:
            help_msg = (
                "No GPU available or CUDA not configured. "
                "THEMIS requires a GPU with ~13GB VRAM for inference.\n"
                "Install CUDA: https://developer.nvidia.com/cuda-downloads\n"
                f"Details: {e}"
            )
        elif "memory" in error_msg or "oom" in error_msg:
            help_msg = (
                "Insufficient GPU memory. THEMIS requires ~13GB VRAM.\n"
                "Close other GPU-intensive applications and try again.\n"
                f"Details: {e}"
            )
        elif (
            "download" in error_msg or "connect" in error_msg or "network" in error_msg
        ):
            help_msg = (
                "Failed to download model weights. Check your internet connection.\n"
                f"Details: {e}"
            )
        else:
            help_msg = f"Failed to load THEMIS model: {e}"

        logger.error(help_msg)
        raise RuntimeError(help_msg) from e


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


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    """Health check endpoint for container orchestration and monitoring."""
    from themis_mcp.tools import _model

    status = "healthy" if _model is not None else "starting"
    code = 200 if _model is not None else 503

    return JSONResponse(
        {
            "status": status,
            "service": "themis-mcp",
            "model_loaded": _model is not None,
        },
        status_code=code,
    )


if "ask" in _enabled_tools:

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


if "lookup" in _enabled_tools:

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


@mcp.prompt()
def compare_ipc_bns(section: str) -> list:
    """Compare an IPC section with its BNS equivalent.

    Args:
        section: IPC section number (e.g. "302", "376")
    """
    from themis_mcp.prompts import ipc_bns_compare

    return ipc_bns_compare(section)


@mcp.prompt()
def explain_section(act: str, section: str) -> list:
    """Explain a specific section in plain language.

    Args:
        act: Act name (e.g. "BNS", "IPC", "BNSS")
        section: Section number
    """
    from themis_mcp.prompts import explain_section as _explain

    return _explain(act, section)


@mcp.prompt()
def punishment_for(act: str, offense: str) -> list:
    """Find the punishment for a specific offense.

    Args:
        act: Act name (e.g. "BNS", "IPC")
        offense: Offense name (e.g. "murder", "theft", "robbery")
    """
    from themis_mcp.prompts import punishment_for_offense

    return punishment_for_offense(act, offense)


@mcp.prompt()
def rti_rights(section: str = "6") -> list:
    """RTI citizen rights query template.

    Args:
        section: RTI section number (default: "6" - Right to information)
    """
    from themis_mcp.prompts import right_know

    return right_know(section)


@mcp.prompt()
def consumer_complaint() -> list:
    """Consumer complaint filing guide."""
    from themis_mcp.prompts import consumer_complaint as _complaint

    return _complaint()


@mcp.prompt()
def section_summary(act: str, section: str) -> list:
    """Quick section lookup with legal significance.

    Args:
        act: Act identifier (e.g. "bns", "ipc", "bnss", "bsa")
        section: Section number
    """
    from themis_mcp.prompts import section_lookup

    return section_lookup(act, section)


def main() -> None:
    """Entry point for the MCP server.

    Transport is configured via environment variables:
        THEMIS_MCP_TRANSPORT: "stdio" (default) or "streamable-http"
        THEMIS_MCP_HOST: Host to bind to (default: "0.0.0.0")
        THEMIS_MCP_PORT: Port to listen on (default: 8000)
    """
    transport = os.environ.get("THEMIS_MCP_TRANSPORT", "stdio")

    if transport == "streamable-http":
        import uvicorn

        host = os.environ.get("THEMIS_MCP_HOST", "0.0.0.0")
        port = int(os.environ.get("THEMIS_MCP_PORT", "8000"))
        logger.info(f"Starting THEMIS MCP on {host}:{port} (Streamable HTTP)")
        app = mcp.streamable_http_app()
        uvicorn.run(app, host=host, port=port)
    else:
        logger.info("Starting THEMIS MCP (stdio)")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
