"""Transform hub catalog and merge."""
from plugins.registry import PluginRegistry
from services.transform_hub import load_catalog, merge_hub_with_plugins, api_key_help


def test_catalog_loads():
    entries = load_catalog()
    assert len(entries) >= 30
    ids = {e["id"] for e in entries}
    assert "hub_hibp" in ids
    assert "hub_virustotal" in ids


def test_api_key_help_includes_signup_links():
    help_items = api_key_help(["HIBP_API_KEY", "SHODAN_API_KEY"])
    by_key = {h["env_key"]: h for h in help_items}
    assert by_key["HIBP_API_KEY"]["signup_url"]
    assert "haveibeenpwned" in by_key["HIBP_API_KEY"]["signup_url"]


def test_merge_marks_installed_plugins():
    PluginRegistry.load_plugins()
    manifests = PluginRegistry.get_all_manifests()
    merged = merge_hub_with_plugins(manifests)
    assert merged["stats"]["installed"] >= 10
    hibp = next(e for e in merged["entries"] if e["id"] == "hub_hibp")
    assert hibp["installed"] is True
    assert hibp.get("plugin", {}).get("id") == "hibp_lookup"
