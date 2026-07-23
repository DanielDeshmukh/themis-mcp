"""MCP prompts for common legal queries."""

from __future__ import annotations

from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent


def _msg(role: str, text: str) -> base.Message:
    return base.Message(role=role, content=TextContent(type="text", text=text))


def ipc_bns_compare(section_number: str) -> list[base.Message]:
    """Compare an IPC section with its BNS equivalent."""
    return [
        _msg(
            "user",
            f"Compare IPC Section {section_number} with its equivalent in the "
            f"Bharatiya Nyaya Sanhita (BNS). What are the key differences in "
            f"wording, punishment, and scope?",
        )
    ]


def explain_section(act: str, section_number: str) -> list[base.Message]:
    """Explain a specific section in plain language."""
    return [
        _msg(
            "user",
            f"Explain {act} Section {section_number} in plain language. "
            f"What does it prohibit, who does it apply to, and what is the punishment?",
        )
    ]


def punishment_for_offense(act: str, offense: str) -> list[base.Message]:
    """Find the punishment for a specific offense."""
    return [
        _msg(
            "user",
            f"What is the punishment for {offense} under the {act}? "
            f"Include the section number, imprisonment term, and any fines.",
        )
    ]


def right_know(
    section_number: str = "6",
) -> list[base.Message]:
    """RTI query template."""
    return [
        _msg(
            "user",
            f"Explain Section {section_number} of the Right to Information Act, 2005. "
            f"What are a citizen's rights and the government's obligations?",
        )
    ]


def consumer_complaint() -> list[base.Message]:
    """Consumer complaint query template."""
    return [
        _msg(
            "user",
            "How do I file a complaint under the Consumer Protection Act, 2019? "
            "What are the grounds, the forum hierarchy, and the time limits?",
        )
    ]


def section_lookup(act: str, section_number: str) -> list[base.Message]:
    """Quick section lookup with context."""
    return [
        _msg(
            "user",
            f"Look up {act} Section {section_number} and explain its legal "
            f"significance. What are the key provisions?",
        )
    ]
