"""
OsintGraph — SQLite Client (offline fallback for graph persistence)
"""
import json
import aiosqlite
import os

DB_PATH = os.getenv("SQLITE_PATH", "osintgraph.db")


class SQLiteClient:
    async def _get_db(self):
        db = await aiosqlite.connect(DB_PATH)
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS graphs (
                workspace_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.commit()
        return db

    async def save_graph(self, workspace_id: str, data: dict):
        async with await self._get_db() as db:
            await db.execute(
                "INSERT OR REPLACE INTO graphs (workspace_id, data, updated_at) VALUES (?, ?, datetime('now'))",
                (workspace_id, json.dumps(data))
            )
            await db.commit()

    async def load_graph(self, workspace_id: str) -> dict:
        async with await self._get_db() as db:
            async with db.execute(
                "SELECT data FROM graphs WHERE workspace_id = ?", (workspace_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return {"nodes": [], "edges": []}

    async def add_node(self, workspace_id: str, node: dict):
        data = await self.load_graph(workspace_id)
        data["nodes"] = [n for n in data["nodes"] if n["id"] != node["id"]]
        data["nodes"].append(node)
        await self.save_graph(workspace_id, data)

    async def delete_node(self, workspace_id: str, node_id: str):
        data = await self.load_graph(workspace_id)
        data["nodes"] = [n for n in data["nodes"] if n["id"] != node_id]
        data["edges"] = [e for e in data["edges"] if e["source"] != node_id and e["target"] != node_id]
        await self.save_graph(workspace_id, data)

    async def add_edge(self, workspace_id: str, edge: dict):
        data = await self.load_graph(workspace_id)
        data["edges"] = [e for e in data["edges"] if e["id"] != edge["id"]]
        data["edges"].append(edge)
        await self.save_graph(workspace_id, data)

    async def delete_workspace(self, workspace_id: str):
        async with await self._get_db() as db:
            await db.execute("DELETE FROM graphs WHERE workspace_id = ?", (workspace_id,))
            await db.commit()

    async def list_workspaces(self) -> list[str]:
        async with await self._get_db() as db:
            async with db.execute("SELECT workspace_id FROM graphs") as cursor:
                rows = await cursor.fetchall()
                return [r[0] for r in rows]


sqlite_client = SQLiteClient()
