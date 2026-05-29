"""
OsintGraph — Workspaces Router
"""
from fastapi import APIRouter
from pydantic import BaseModel
from db.sqlite_client import sqlite_client

router = APIRouter()


class WorkspaceCreate(BaseModel):
    name: str


@router.get("")
async def list_workspaces():
    workspaces = await sqlite_client.list_workspaces()
    if "default" not in workspaces:
        workspaces = ["default"] + workspaces
    return {"workspaces": workspaces}


@router.post("")
async def create_workspace(body: WorkspaceCreate):
    # Initialize empty graph for workspace
    await sqlite_client.save_graph(body.name, {"nodes": [], "edges": []})
    return {"created": body.name}


@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: str):
    if workspace_id == "default":
        return {"error": "Cannot delete default workspace"}
    await sqlite_client.delete_workspace(workspace_id)
    return {"deleted": workspace_id}
