import pytest

from services.web_search_results import _dedupe_findings, findings_to_graph


def test_dedupe_findings():
    items = [
        {"url": "https://a.test", "title": "A"},
        {"url": "https://a.test", "title": "dup"},
        {"url": "https://b.test", "title": "B"},
    ]
    out = _dedupe_findings(items)
    assert len(out) == 2


def test_findings_to_graph_creates_real_pages_not_engines():
    findings = [{
        "title": "Sherlyn Grewal — Example Profile",
        "url": "https://www.linkedin.com/in/example",
        "snippet": "Public profile snippet",
        "source_engine": "brave",
    }]
    nodes, edges, obs = findings_to_graph("Sherlyn Grewal", findings, "web_search")
    assert len(nodes) == 1
    assert nodes[0]["label"] != "Google"
    assert "linkedin" in nodes[0]["properties"]["url"]
