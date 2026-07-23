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
