import asyncio
import json
from db.sqlite_client import sqlite_client
from db.domain_client import DomainClient

async def main():
    d_client = DomainClient()
    workspace_id = "7133911a-66bf-4d95-b8b2-51ca7dd0fcc6"
    print("Loading graph...")
    graph = await sqlite_client.load_graph(workspace_id)
    print(f"Graph has {len(graph.get('nodes', []))} nodes and {len(graph.get('edges', []))} edges.")
    try:
        await d_client.sync_workspace_to_dossier(workspace_id, graph)
        print("Sync completed successfully.")
    except Exception as e:
        print(f"Exception during sync: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
