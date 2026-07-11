"""
OsintGraph — Transforms Router
"""
from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Any
from transforms.base import list_transforms, get_transform, autodiscover

autodiscover()

router = APIRouter()


class TransformRequest(BaseModel):
    transform: str
    input_type: str
    value: str
    node_id: str | None = None
    options: dict[str, Any] = {}


@router.get("")
async def get_transforms():
    """List all available transforms."""
    return list_transforms()


@router.post("/run")
async def run_transform(req: TransformRequest, request: Request):
    """Execute a transform and return results. Also emits via Socket.IO."""
    transform = get_transform(req.transform)
    if not transform:
        return {"ok": False, "error": f"Transform '{req.transform}' not found"}

    sio = request.app.state.sio

    # Emit start event
    await sio.emit("transform:start", {
        "transform": req.transform,
        "node_id": req.node_id,
        "value": req.value,
    })

    try:
        result = await transform.run(req.value, req.options)
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
        await sio.emit("transform:error", {
            "transform": req.transform,
            "node_id": req.node_id,
            "error": str(e),
        })
        return {"ok": False, "error": str(e), "nodes": [], "edges": [], "log": [f"Error: {e}"]}
