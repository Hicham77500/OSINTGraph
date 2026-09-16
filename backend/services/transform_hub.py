"""Maltego-style transform hub catalog — maps partners to OSINTGraph plugins."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_CATALOG_PATH = Path(__file__).resolve().parent.parent / "config" / "transform_hub_catalog.json"


def _catalog_path() -> Path:
    return _CATALOG_PATH


def load_catalog() -> list[dict[str, Any]]:
    path = _catalog_path()
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def env_configured(env_keys: list[str] | None) -> bool:
    if not env_keys:
        return True
    return all(bool(os.getenv(k)) for k in env_keys)


def plugin_env_keys(plugin_id: str, providers: list[str] | None) -> list[str]:
    for item in load_catalog():
        if item.get("plugin_id") == plugin_id and item.get("env_keys"):
            return list(item["env_keys"])
    if providers:
        return [f"{p.upper()}_API_KEY" for p in providers]
    return []


def merge_hub_with_plugins(
    plugin_manifests: list[dict[str, Any]],
) -> dict[str, Any]:
    installed_ids = {m.get("id") for m in plugin_manifests if m.get("id")}
    catalog = load_catalog()
    plugins_by_id = {m["id"]: m for m in plugin_manifests if m.get("id")}

    entries: list[dict[str, Any]] = []
    for item in catalog:
        pid = item.get("plugin_id")
        entry = {**item}
        if pid:
            entry["installed"] = pid in installed_ids
            if pid in plugins_by_id:
                entry["plugin"] = plugins_by_id[pid]
        else:
            entry["installed"] = False
        entry["configured"] = env_configured(item.get("env_keys") or [])
        entries.append(entry)

    available = sum(1 for e in entries if e.get("installed"))
    configured = sum(1 for e in entries if e.get("installed") and e.get("configured"))
    return {
        "entries": entries,
        "stats": {
            "total": len(entries),
            "installed": available,
            "configured": configured,
        },
    }
