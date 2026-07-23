"""Optional OpenTelemetry tracing for THEMIS MCP tools."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator

logger = logging.getLogger("themis_mcp")

_tracer: Any = None


def init_tracer(service_name: str = "themis-mcp") -> bool:
    """Initialize OpenTelemetry tracer if available.

    Returns True if tracer was initialized, False otherwise.
    """
    global _tracer

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        provider = TracerProvider()
        provider.add_span_processor(
            __import__(
                "opentelemetry.sdk.trace.export",
                fromlist=["BatchSpanProcessor"],
            ).BatchSpanProcessor(ConsoleSpanExporter())
        )
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(service_name)
        logger.info("OpenTelemetry tracer initialized.")
        return True
    except ImportError:
        logger.debug("OpenTelemetry not installed. Tracing disabled.")
        return False
    except Exception as e:
        logger.warning(f"Failed to initialize OpenTelemetry: {e}")
        return False


@contextmanager
def trace_tool(tool_name: str, **attributes: Any) -> Iterator[None]:
    """Context manager to trace a tool call.

    Usage:
        with trace_tool("themis_ask", question=question):
            response = model.ask(question)
    """
    if _tracer is None:
        yield
        return

    with _tracer.start_as_current_span(
        f"mcp.tool.{tool_name}",
        attributes={
            "mcp.tool.name": tool_name,
            **{f"mcp.tool.{k}": str(v) for k, v in attributes.items()},
        },
    ) as span:
        try:
            yield
            span.set_status(__import__("opentelemetry.trace", fromlist=["StatusCode"]).StatusCode.OK)
        except Exception as e:
            span.set_status(
                __import__("opentelemetry.trace", fromlist=["StatusCode"]).StatusCode.ERROR,
                str(e),
            )
            raise
