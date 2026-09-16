"""Transform hub catalog and merge."""
from plugins.registry import PluginRegistry
from services.transform_hub import load_catalog, merge_hub_with_plugins


def test_catalog_loads():
    entries = load_catalog()
    assert len(entries) >= 30
    ids = {e["id"] for e in entries}
    assert "hub_hibp" in ids
    assert "hub_virustotal" in ids


def test_merge_marks_installed_plugins():
    PluginRegistry.load_plugins()
    manifests = PluginRegistry.get_all_manifests()
    merged = merge_hub_with_plugins(manifests)
    assert merged["stats"]["installed"] >= 10
    hibp = next(e for e in merged["entries"] if e["id"] == "hub_hibp")
    assert hibp["installed"] is True
    assert hibp.get("plugin", {}).get("id") == "hibp_lookup"
