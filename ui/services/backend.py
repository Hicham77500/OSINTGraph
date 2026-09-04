"""Bridge vers le backend OSINTGraph (appels directs, sans HTTP)."""
from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# Rendre le backend importable
_BACKEND = Path(__file__).resolve().parents[2] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

os.environ.setdefault("SQLITE_PATH", str(_BACKEND.parent / "data" / "osintgraph.db"))

from db.domain_client import domain_client  # noqa: E402
from db.sqlite_client import sqlite_client  # noqa: E402
from models.domain import (  # noqa: E402
    CarnetCreate,
    DossierCreate,
    EntityCreate,
    EntityUpdate,
    NotebookType,
)
from plugins.base import PluginContext  # noqa: E402
from plugins.registry import PluginRegistry  # noqa: E402
from services.ai_analysis import analyze_entity  # noqa: E402
from services.api_manager import api_manager  # noqa: E402
from services.context_readiness import compute_readiness  # noqa: E402
from services import entity_resolution  # noqa: E402

logger = logging.getLogger("osintgraph.streamlit")
ACTOR = "streamlit-analyst"

_initialized = False


class _DummyEntity:
    def __init__(self, label: str):
        self.label = label


def run_async(coro):
    """Exécute une coroutine depuis Streamlit (sync)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
    except RuntimeError:
        pass
    return asyncio.run(coro)


def ensure_backend() -> None:
    global _initialized
    if _initialized:
        return
    db_path = os.environ["SQLITE_PATH"]
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    run_async(domain_client.init_schema())
    run_async(domain_client.ensure_default_dossier())
    _initialized = True


# ── Dossiers ──────────────────────────────────────────────────────────

def list_dossiers():
    ensure_backend()
    return run_async(domain_client.list_dossiers())


def list_trash_dossiers():
    ensure_backend()
    return run_async(domain_client.list_deleted_dossiers())


def get_dossier(dossier_id: str):
    ensure_backend()
    return run_async(domain_client.get_dossier(dossier_id))


def create_dossier(name: str, description: str | None = None):
    ensure_backend()
    return run_async(domain_client.create_dossier(DossierCreate(name=name, description=description), actor=ACTOR))


def soft_delete_dossier(dossier_id: str):
    ensure_backend()
    return run_async(domain_client.soft_delete_dossier(dossier_id, actor=ACTOR))


def restore_dossier(dossier_id: str):
    ensure_backend()
    return run_async(domain_client.restore_dossier(dossier_id, actor=ACTOR))


def permanent_delete_dossier(dossier_id: str):
    ensure_backend()
    return run_async(domain_client.permanent_delete_dossier(dossier_id, actor=ACTOR))


# ── Carnets ─────────────────────────────────────────────────────────

def list_carnets(dossier_id: str):
    ensure_backend()
    return run_async(domain_client.list_carnets(dossier_id))


def create_carnet(dossier_id: str, name: str, notebook_type: str = "custom"):
    ensure_backend()
    return run_async(
        domain_client.create_carnet(
            dossier_id,
            CarnetCreate(name=name, notebook_type=NotebookType(notebook_type)),
            actor=ACTOR,
        )
    )


# ── Entités ─────────────────────────────────────────────────────────

def list_entities(dossier_id: str, carnet_id: str | None = None, entity_type: str | None = None):
    ensure_backend()
    return run_async(domain_client.list_entities(dossier_id, carnet_id, entity_type))


def get_entity(entity_id: str):
    ensure_backend()
    return run_async(domain_client.get_entity(entity_id))


def create_entity(dossier_id: str, data: dict):
    ensure_backend()
    return run_async(
        domain_client.create_entity(dossier_id, EntityCreate(**data), actor=ACTOR)
    )


def update_entity(entity_id: str, data: dict):
    ensure_backend()
    return run_async(
        domain_client.update_entity(entity_id, EntityUpdate(**data), actor=ACTOR)
    )


def delete_entity(entity_id: str):
    ensure_backend()
    return run_async(domain_client.delete_entity(entity_id, actor=ACTOR))


def get_observations(entity_id: str):
    ensure_backend()
    return run_async(domain_client.get_observations_for_entity(entity_id))


def get_entity_relations(entity_id: str):
    ensure_backend()
    entity = run_async(domain_client.get_entity(entity_id))
    return run_async(domain_client.list_relations(entity.dossier_id, entity_id))


def get_readiness(entity_id: str):
    ensure_backend()
    return run_async(compute_readiness(entity_id))


def run_ai_analysis(entity_id: str):
    ensure_backend()
    return run_async(analyze_entity(entity_id))


# ── Recherche ───────────────────────────────────────────────────────

def global_search(query: str, limit: int = 20):
    ensure_backend()
    return run_async(domain_client.search(query, limit))


# ── Graphe ──────────────────────────────────────────────────────────

def load_graph(workspace_id: str) -> dict[str, Any]:
    ensure_backend()
    return run_async(sqlite_client.load_graph(workspace_id))


def save_graph(workspace_id: str, data: dict[str, Any]) -> None:
    ensure_backend()
    run_async(sqlite_client.save_graph(workspace_id, data))
    try:
        run_async(domain_client.sync_workspace_to_dossier(workspace_id, data))
    except Exception as exc:
        logger.warning("Sync workspace→dossier failed: %s", exc)


# ── Transforms / Plugins ────────────────────────────────────────────

def list_transforms() -> list[dict]:
    ensure_backend()
    manifests = PluginRegistry.get_all_manifests()
    return [
        {
            "id": m.get("id"),
            "name": m.get("name"),
            "description": m.get("description"),
            "category": m.get("category"),
            "input_types": m.get("input_types", []),
            "output_types": m.get("output_types", []),
        }
        for m in manifests
    ]


def run_transform(transform_id: str, value: str, options: dict | None = None) -> dict:
    ensure_backend()
    plugin = PluginRegistry.get_plugin_instance(transform_id)
    if not plugin:
        return {"ok": False, "error": f"Plugin '{transform_id}' introuvable", "nodes": [], "edges": [], "log": []}

    async def _run():
        context = PluginContext(
            entity=_DummyEntity(value),
            api_manager=api_manager,
            logger=logger,
            config=options or {},
        )
        result = await plugin.run(context)
        result.setdefault("observations", [])
        result.setdefault("nodes", [])
        result.setdefault("edges", [])
        result.setdefault("log", [])
        return {"ok": True, "transform": transform_id, **result}

    try:
        return run_async(_run())
    except Exception as exc:
        logger.error("Transform %s failed: %s", transform_id, exc)
        return {"ok": False, "error": str(exc), "nodes": [], "edges": [], "log": [str(exc)]}


# ── Merge suggestions ───────────────────────────────────────────────

def get_merge_suggestions(dossier_id: str):
    ensure_backend()
    run_async(entity_resolution.find_duplicates(dossier_id))
    return run_async(entity_resolution.list_suggestions(dossier_id))


def seed_demo_dossier(force: bool = False) -> tuple[str, bool]:
    """Exécute le script de seed démo. Retourne (message, succès)."""
    ensure_backend()
    script = _BACKEND / "scripts" / "seed_test_dossier.py"
    if not script.exists():
        return "Script de démo introuvable.", False

    cmd = [sys.executable, str(script)]
    if force:
        cmd.append("--force")

    result = subprocess.run(
        cmd,
        cwd=str(_BACKEND),
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or result.stderr or "").strip()
    if result.returncode == 0:
        if "skipped" in output.lower():
            return "Dossier TEST déjà présent — ouvrez-le dans la liste.", True
        return output.split("\n")[0] or "Dossier de démo chargé.", True
    return output or "Échec du chargement de la démo.", False
