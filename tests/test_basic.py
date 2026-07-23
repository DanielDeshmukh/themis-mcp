"""Basic tests for themis-mcp."""

import json


def test_import():
    """Package imports successfully."""
    import themis_mcp

    assert themis_mcp.__version__ == "0.1.0"


def test_disclaimer():
    """Disclaimer resource returns expected text."""
    from themis_mcp.resources import get_disclaimer

    text = get_disclaimer()
    assert "not legal advice" in text
    assert "qualified lawyer" in text


def test_acts():
    """Acts resource returns valid JSON with expected keys."""
    from themis_mcp.resources import get_acts

    acts = json.loads(get_acts())
    assert "bns" in acts
    assert "ipc" in acts
    assert "bnss" in acts
    assert "bsa" in acts
    assert acts["bns"]["sections"] == 358


def test_prompts():
    """Prompts module returns valid message lists."""
    from themis_mcp.prompts import (
        consumer_complaint,
        explain_section,
        ipc_bns_compare,
        punishment_for_offense,
        right_know,
        section_lookup,
    )

    assert len(ipc_bns_compare("302")) == 1
    assert len(explain_section("BNS", "103")) == 1
    assert len(punishment_for_offense("BNS", "murder")) == 1
    assert len(right_know("6")) == 1
    assert len(consumer_complaint()) == 1
    assert len(section_lookup("bns", "103")) == 1

    for messages in [
        ipc_bns_compare("302"),
        explain_section("BNS", "103"),
        punishment_for_offense("BNS", "murder"),
        right_know("6"),
        consumer_complaint(),
        section_lookup("bns", "103"),
    ]:
        assert isinstance(messages, list)
        assert messages[0].role == "user"
