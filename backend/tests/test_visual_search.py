from services.visual_search import build_search_assistants


def test_assistants_include_manual_providers():
    items = build_search_assistants(None)
    ids = {i["id"] for i in items}
    assert "google_lens" in ids
    assert "tineye" in ids


def test_assistants_url_mode_when_public_url():
    url = "https://example.com/a.jpg"
    items = build_search_assistants(url)
    by_id = {i["id"]: i for i in items}
    assert "google_by_url" in by_id
    assert "searchbyimage" in by_id["google_by_url"]["url"]
    assert "example.com" in by_id["google_by_url"]["url"]
