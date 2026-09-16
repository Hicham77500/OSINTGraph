from services.general_search import (
    build_forum_keyword_links,
    build_social_platform_links,
    build_vehicle_plate_links,
    build_web_browser_links,
)


def test_web_browsers_count():
    assert len(build_web_browser_links("test query")) >= 8


def test_social_includes_facebook():
    links = build_social_platform_links("jdupont")
    assert any("facebook" in l["id"] for l in links)


def test_forum_keyword_pirate():
    links = build_forum_keyword_links("user123", ["pirate"])
    assert any("pirate" in l.get("keyword", "") for l in links)
    assert any("reddit.com" in l["url"] for l in links)


def test_plate_no_fake_registry_data():
    links = build_vehicle_plate_links("AB-123-CD")
    assert all("url" in l for l in links)
