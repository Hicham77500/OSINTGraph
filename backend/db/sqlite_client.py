"""
OsintGraph — SQLite Client (offline fallback for graph persistence)
"""
import json
import aiosqlite
import os

DB_PATH = os.getenv("SQLITE_PATH", "osintgraph.db")


def _db_path() -> str:
    return os.getenv("SQLITE_PATH", "osintgraph.db")


class SQLiteClient:
    async def _connect(self):
        db = await aiosqlite.connect(_db_path())
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS graphs (
                workspace_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        return db

    async def save_graph(self, workspace_id: str, data: dict):
        db = await self._connect()
        try:
            await db.execute(
                "INSERT OR REPLACE INTO graphs (workspace_id, data, updated_at) VALUES (?, ?, datetime('now'))",
                (workspace_id, json.dumps(data))
            )
            await db.commit()
        finally:
            await db.close()

    async def load_graph(self, workspace_id: str) -> dict:
        db = await self._connect()
        try:
            async with db.execute(
                "SELECT data FROM graphs WHERE workspace_id = ?", (workspace_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return {"nodes": [], "edges": []}
        finally:
            await db.close()

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
        db = await self._connect()
        try:
            await db.execute("DELETE FROM graphs WHERE workspace_id = ?", (workspace_id,))
            await db.commit()
        finally:
            await db.close()

    async def list_workspaces(self) -> list[str]:
        db = await self._connect()
        try:
            async with db.execute("SELECT workspace_id FROM graphs") as cursor:
                rows = await cursor.fetchall()
                return [r[0] for r in rows]
        finally:
            await db.close()


sqlite_client = SQLiteClient()
