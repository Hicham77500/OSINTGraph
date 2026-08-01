"""Tests for plugin registry and new OSINT transforms."""
import pytest

from plugins.registry import PluginRegistry


@pytest.fixture(autouse=True)
def reload_plugins():
    PluginRegistry.load_plugins()
    yield


EXPECTED_PLUGINS = {
    "sherlock_lookup",
    "shodan_lookup",
    "ip_geolocation",
    "phone_lookup",
    "holehe_lookup",
    "dns_lookup",
    "whois_lookup",
    "maigret_lookup",
    "spiderfoot_scan",
}


def test_all_plugins_discovered():
    manifests = PluginRegistry.get_all_manifests()
    ids = {m["id"] for m in manifests}
    assert EXPECTED_PLUGINS.issubset(ids)


@pytest.mark.parametrize("plugin_id", sorted(EXPECTED_PLUGINS))
def test_plugin_loads(plugin_id):
    instance = PluginRegistry.get_plugin_instance(plugin_id)
    assert instance is not None
    assert hasattr(instance, "run")


def test_holehe_input_types():
    manifest = next(m for m in PluginRegistry.get_all_manifests() if m["id"] == "holehe_lookup")
    assert "EMAIL" in manifest["input_types"]


def test_spiderfoot_passive_default_modules():
    from plugins.spiderfoot_scan.plugin import DEFAULT_PASSIVE_MODULES
    assert "sfp_dnsresolve" in DEFAULT_PASSIVE_MODULES
    assert "sfp_whois" in DEFAULT_PASSIVE_MODULES
