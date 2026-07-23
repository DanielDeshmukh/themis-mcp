"""MCP sampling support for AI-assisted clarification."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import Context

logger = logging.getLogger("themis_mcp")


async def sample_clarification(
    ctx: Context,
    question: str,
    ambiguous_part: str,
) -> str | None:
    """Ask the client's LLM to clarify an ambiguous question.

    Uses MCP sampling to request the client's LLM to resolve ambiguity
    before the server's model processes the question.

    Args:
        ctx: MCP context with session access
        question: The original user question
        ambiguous_part: The specific part that needs clarification

    Returns:
        Clarified text or None if sampling fails or client doesn't support it
    """
    try:
        from mcp.types import SamplingMessage, TextContent

        messages = [
            SamplingMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=(
                        f"The following legal question has an ambiguous part. "
                        f"Please clarify what the user likely means.\n\n"
                        f"Question: {question}\n"
                        f"Ambiguous part: {ambiguous_part}\n\n"
                        f"Provide a brief clarification (1-2 sentences)."
                    ),
                ),
            )
        ]

        result = await ctx.session.create_message(
            messages=messages,
            max_tokens=100,
            system_prompt=(
                "You are a legal assistant helping clarify ambiguous questions "
                "about Indian statutory law. Be concise."
            ),
        )

        if hasattr(result, "content") and hasattr(result.content, "text"):
            return result.content.text  # type: ignore[no-any-return]
        return None

    except Exception as e:
        logger.debug(f"Sampling failed (client may not support it): {e}")
        return None


async def sample_follow_up(
    ctx: Context,
    initial_answer: str,
    user_question: str,
) -> str | None:
    """Generate a follow-up question using the client's LLM.

    Uses MCP sampling to suggest a follow-up question based on the
    initial answer provided.

    Args:
        ctx: MCP context with session access
        initial_answer: The answer already provided
        user_question: The original user question

    Returns:
        Suggested follow-up question or None if sampling fails
    """
    try:
        from mcp.types import SamplingMessage, TextContent

        messages = [
            SamplingMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=(
                        f"Based on this legal Q&A, suggest one relevant follow-up "
                        f"question the user might want to ask.\n\n"
                        f"Question: {user_question}\n"
                        f"Answer: {initial_answer[:500]}\n\n"
                        f"Suggest a brief follow-up question (1 sentence)."
                    ),
                ),
            )
        ]

        result = await ctx.session.create_message(
            messages=messages,
            max_tokens=50,
            system_prompt="You are a legal assistant. Suggest concise follow-up questions.",
        )

        if hasattr(result, "content") and hasattr(result.content, "text"):
            return result.content.text  # type: ignore[no-any-return]
        return None

    except Exception as e:
        logger.debug(f"Sampling failed: {e}")
        return None
