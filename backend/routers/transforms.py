"""
OsintGraph — Plugins Router
"""
import asyncio
import logging
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Any

from plugins.registry import PluginRegistry
from plugins.base import PluginContext
from services.api_manager import api_manager

logger = logging.getLogger("osintgraph.router.plugins")
router = APIRouter()


class TransformRequest(BaseModel):
    transform: str
    input_type: str
    value: str
    node_id: str | None = None
    options: dict[str, Any] = {}


# Mock Entity class for PluginContext
class DummyEntity:
    def __init__(self, label: str):
        self.label = label


@router.get("")
async def get_transforms():
    """List all available plugins (transforms)."""
    # PluginRegistry parses manifest which returns a dict
    # the frontend expects a list of dicts.
    manifests = PluginRegistry.get_all_manifests()
    # Format them for the frontend
    result = []
    for m in manifests:
        result.append({
            "id": m.get("id"),
            "name": m.get("name"),
            "description": m.get("description"),
            "category": m.get("category"),
            "input_types": m.get("input_types", []),
            "output_types": m.get("output_types", []),
            "permissions": m.get("permissions", []),
            "providers": m.get("providers", []),
        })
    return result


@router.post("/run")
async def run_transform(req: TransformRequest, request: Request):
    """Execute a plugin transform and return results."""
    plugin = PluginRegistry.get_plugin_instance(req.transform)
    if not plugin:
        return {"ok": False, "error": f"Plugin '{req.transform}' not found"}

    sio = request.app.state.sio
    event_base = {
        "transform": req.transform,
        "node_id": req.node_id,
    }

    async def emit_log(message: str, current: int = 0, total: int = 0) -> None:
        payload = {**event_base, "message": message}
        if current or total:
            payload["current"] = current
            payload["total"] = total
            await sio.emit("transform:progress", payload)
        await sio.emit("transform:log", payload)

    def progress_callback(current: int, total: int, message: str) -> None:
        asyncio.get_running_loop().create_task(emit_log(message, current, total))

    # Emit start event
    await sio.emit("transform:start", {
        **event_base,
        "value": req.value,
    })

    try:
        context = PluginContext(
            entity=DummyEntity(req.value),  # Simple entity wrapper
            api_manager=api_manager,
            logger=logger,
            config=req.options,
            progress_callback=progress_callback,
        )
        
        result = await plugin.run(context)
        result.setdefault("observations", [])

        await sio.emit("transform:result", {
            "transform": req.transform,
            "node_id": req.node_id,
            **result,
        })

        return {
            "ok": True,
            "transform": req.transform,
            "node_id": req.node_id,
            **result,
        }
    except Exception as e:
        logger.error(f"Error running plugin {req.transform}: {e}")
        await sio.emit("transform:error", {
            "transform": req.transform,
            "node_id": req.node_id,
            "error": str(e),
        })
        return {"ok": False, "error": str(e), "nodes": [], "edges": [], "log": [f"Error: {e}"]}
