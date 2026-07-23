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


def test_structured_output():
    """Structured output types serialize correctly."""
    from themis_mcp.structured import LookupResult, ToolResult

    result = ToolResult(
        text="Section 103 defines murder.",
        grounded=True,
        section="103",
        act="BNS",
        confidence=0.95,
    )
    d = result.to_dict()
    assert d["text"] == "Section 103 defines murder."
    assert d["grounded"] is True
    assert d["section"] == "103"
    assert "warning" not in d

    j = result.to_json()
    assert '"text": "Section 103 defines murder."' in j

    lookup = LookupResult(
        found=True,
        section_number="103",
        act_name="BNS",
        text="103. Murder...",
    )
    ld = lookup.to_dict()
    assert ld["found"] is True
    assert ld["section_number"] == "103"

    not_found = LookupResult(found=False, text="Not found.")
    assert not_found.to_dict()["found"] is False


def test_cache():
    """Cache module stores and retrieves values correctly."""
    from themis_mcp.cache import CacheConfig, ResponseCache

    cache = ResponseCache(CacheConfig(max_size=2, ttl_seconds=1.0))

    cache.set("test", "value1", arg="a")
    assert cache.get("test", arg="a") == "value1"
    assert cache.get("test", arg="b") is None

    stats = cache.stats
    assert stats["size"] == 1
    assert stats["hits"] == 1
    assert stats["misses"] == 1

    cache.clear()
    assert cache.get("test", arg="a") is None
    assert cache.stats["size"] == 0


def test_metrics():
    """Metrics module tracks and formats metrics correctly."""
    from themis_mcp.metrics import MetricsCollector

    m = MetricsCollector()

    m.inc_counter("test_counter")
    m.inc_counter("test_counter")
    m.set_gauge("test_gauge", 42.0)
    m.observe_histogram("test_histogram", 0.5)
    m.observe_histogram("test_histogram", 1.5)

    output = m.to_prometheus()
    assert "test_counter 2.0" in output
    assert "test_gauge 42.0" in output
    assert "test_histogram_count 2" in output
    assert "test_histogram_sum 2.0" in output
    assert "themis_uptime_seconds" in output


def test_sessions():
    """Session manager creates, retrieves, and cleans up sessions."""
    from themis_mcp.sessions import SessionManager

    mgr = SessionManager(timeout=0.1)

    session = mgr.create_session({"user": "test"})
    assert mgr.active_count == 1

    retrieved = mgr.get_session(session.session_id)
    assert retrieved is not None
    assert retrieved.metadata["user"] == "test"

    removed = mgr.remove_session(session.session_id)
    assert removed is True
    assert mgr.active_count == 0

    assert mgr.get_session(session.session_id) is None
