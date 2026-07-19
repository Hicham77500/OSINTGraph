"""
OsintGraph — Graph Router
CRUD endpoints for nodes/edges in a workspace
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Any
from db.sqlite_client import sqlite_client
from db.domain_client import DomainClient

domain_client = DomainClient()

router = APIRouter()


class NodeModel(BaseModel):
    id: str
    type: str
    label: str
    properties: dict[str, str] = {}
    metadata: dict[str, Any] = {}


class EdgeModel(BaseModel):
    id: str
    source: str
    target: str
    type: str
    label: str | None = None


class GraphData(BaseModel):
    nodes: list[NodeModel]
    edges: list[EdgeModel]


@router.get("/{workspace_id}")
async def get_graph(workspace_id: str):
    data = await sqlite_client.load_graph(workspace_id)
    return data


@router.post("/{workspace_id}")
async def save_graph(workspace_id: str, data: GraphData):
    await sqlite_client.save_graph(workspace_id, data.model_dump())
    
    # Synchronize graph elements with relational DB for Dossier Hub stats
    try:
        await domain_client.sync_workspace_to_dossier(workspace_id, data.model_dump())
    except Exception as e:
        print(f"Failed to sync workspace to dossier: {e}")
        
    return {"status": "saved", "nodes": len(data.nodes), "edges": len(data.edges)}


@router.post("/{workspace_id}/nodes")
async def add_node(workspace_id: str, node: NodeModel):
    await sqlite_client.add_node(workspace_id, node.model_dump())
    return node


@router.delete("/{workspace_id}/nodes/{node_id}")
async def delete_node(workspace_id: str, node_id: str):
    await sqlite_client.delete_node(workspace_id, node_id)
    return {"deleted": node_id}


@router.post("/{workspace_id}/edges")
async def add_edge(workspace_id: str, edge: EdgeModel):
    await sqlite_client.add_edge(workspace_id, edge.model_dump())
    return edge
