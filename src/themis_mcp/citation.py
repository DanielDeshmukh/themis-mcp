"""Legal citation formatter for Indian statutes."""

from __future__ import annotations

# Act name mappings for consistent citation
ACT_NAMES = {
    "bns": "The Bharatiya Nyaya Sanhita, 2023",
    "bnss": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
    "bsa": "The Bharatiya Sakshya Adhiniyam, 2023",
    "ipc": "The Indian Penal Code, 1860",
    "rti_2005": "The Right to Information Act, 2005",
    "consumer_protection_2019": "The Consumer Protection Act, 2019",
}

# Short names for display
SHORT_NAMES = {
    "bns": "BNS",
    "bnss": "BNSS",
    "bsa": "BSA",
    "ipc": "IPC",
    "rti_2005": "RTI",
    "consumer_protection_2019": "CPA",
}


def format_citation(
    act: str,
    section: str,
    short: bool = False,
) -> str:
    """Format a legal citation for an Indian statute.

    Args:
        act: Act identifier (e.g. "bns", "ipc", "bnss")
        section: Section number (e.g. "103", "302")
        short: If True, use short act name (e.g. "BNS s. 103")

    Returns:
        Formatted citation string.

    Examples:
        >>> format_citation("bns", "103")
        'Section 103, The Bharatiya Nyaya Sanhita, 2023'
        >>> format_citation("ipc", "302", short=True)
        'IPC s. 302'
    """
    section_clean = section.replace("Section ", "").replace("section ", "").strip()
    act_lower = act.lower()

    if short:
        short_name = SHORT_NAMES.get(act_lower, act.upper())
        return f"{short_name} s. {section_clean}"

    full_name = ACT_NAMES.get(act_lower, act)
    return f"Section {section_clean}, {full_name}"


def format_footnote(
    act: str,
    section: str,
    year: str | None = None,
) -> str:
    """Format a footnote-style citation.

    Args:
        act: Act identifier
        section: Section number
        year: Optional year (extracted from act name if not provided)

    Returns:
        Formatted footnote string.

    Examples:
        >>> format_footnote("bns", "103")
        'Bharatiya Nyaya Sanhita, 2023, s. 103.'
    """
    section_clean = section.replace("Section ", "").replace("section ", "").strip()
    act_lower = act.lower()

    full_name = ACT_NAMES.get(act_lower, act)
    # Remove "The " prefix for footnote style
    if full_name.startswith("The "):
        full_name = full_name[4:]

    return f"{full_name}, s. {section_clean}."


def format_inline_citation(
    act: str,
    section: str,
) -> str:
    """Format an inline parenthetical citation.

    Args:
        act: Act identifier
        section: Section number

    Returns:
        Formatted inline citation.

    Examples:
        >>> format_inline_citation("bns", "103")
        '(BNS, s. 103)'
    """
    section_clean = section.replace("Section ", "").replace("section ", "").strip()
    act_lower = act.lower()

    short_name = SHORT_NAMES.get(act_lower, act.upper())
    return f"({short_name}, s. {section_clean})"
