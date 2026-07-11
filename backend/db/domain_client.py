"""
OSINTGraph — Relational SQLite domain persistence
"""
import json
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

import aiosqlite

from models.domain import (
    CarnetCreate,
    CarnetOut,
    CollectionMethod,
    ConfidenceStatus,
    DossierCreate,
    DossierOut,
    EntityCreate,
    EntityOut,
    EntityType,
    EntityUpdate,
    RelationCreate,
    RelationOut,
    new_id,
)
from db.sqlite_client import sqlite_client

logger = logging.getLogger("osintgraph.db")

DB_PATH = os.getenv("SQLITE_PATH", "osintgraph.db")


def _db_path() -> str:
    return os.getenv("SQLITE_PATH", "osintgraph.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS dossiers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    workspace_id TEXT UNIQUE,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    deleted_at TEXT NULL
);

CREATE TABLE IF NOT EXISTS carnets (
    id TEXT PRIMARY KEY,
    dossier_id TEXT NOT NULL REFERENCES dossiers(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    notebook_type TEXT NOT NULL DEFAULT 'custom',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    dossier_id TEXT NOT NULL REFERENCES dossiers(id) ON DELETE CASCADE,
    carnet_id TEXT REFERENCES carnets(id) ON DELETE SET NULL,
    entity_type TEXT NOT NULL,
    label TEXT NOT NULL,
    properties TEXT DEFAULT '{}',
    confidence REAL DEFAULT 0.5,
    status TEXT DEFAULT 'UNVERIFIED',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    url TEXT,
    collection_method TEXT NOT NULL,
    collected_at TEXT DEFAULT (datetime('now')),
    metadata TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS observations (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    entity_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    observed_at TEXT DEFAULT (datetime('now')),
    confidence REAL DEFAULT 0.5,
    status TEXT DEFAULT 'UNVERIFIED'
);

CREATE TABLE IF NOT EXISTS relations (
    id TEXT PRIMARY KEY,
    dossier_id TEXT NOT NULL REFERENCES dossiers(id) ON DELETE CASCADE,
    source_entity_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    target_entity_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    status TEXT DEFAULT 'UNVERIFIED',
    evidence_ids TEXT DEFAULT '[]',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    observation_id TEXT REFERENCES observations(id) ON DELETE SET NULL,
    relation_id TEXT REFERENCES relations(id) ON DELETE SET NULL,
    hypothesis_id TEXT,
    summary TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    status TEXT DEFAULT 'UNVERIFIED'
);

CREATE TABLE IF NOT EXISTS hypotheses (
    id TEXT PRIMARY KEY,
    dossier_id TEXT NOT NULL REFERENCES dossiers(id) ON DELETE CASCADE,
    entity_id TEXT REFERENCES entities(id) ON DELETE SET NULL,
    claim TEXT NOT NULL,
    reasoning_summary TEXT NOT NULL,
    evidence_ids TEXT DEFAULT '[]',
    confidence REAL DEFAULT 0.5,
    contradictions TEXT DEFAULT '[]',
    status TEXT DEFAULT 'POSSIBLE',
    source TEXT DEFAULT 'SYSTEM',
    analyst_action TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS merge_suggestions (
    id TEXT PRIMARY KEY,
    dossier_id TEXT NOT NULL REFERENCES dossiers(id) ON DELETE CASCADE,
    entity_a_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    entity_b_id TEXT NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    similarity REAL NOT NULL,
    reasons TEXT DEFAULT '[]',
    status TEXT DEFAULT 'PENDING',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    previous_state TEXT,
    new_state TEXT,
    timestamp TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_entities_dossier ON entities(dossier_id);
CREATE INDEX IF NOT EXISTS idx_entities_label ON entities(label);
CREATE INDEX IF NOT EXISTS idx_relations_dossier ON relations(dossier_id);
CREATE INDEX IF NOT EXISTS idx_observations_entity ON observations(entity_id);
"""


DEFAULT_CARNETS = [
    ("Personnes", "personnes"),
    ("Réseaux sociaux", "reseaux_sociaux"),
    ("Organisations", "entreprises"),
    ("Pseudonymes", "pseudonymes"),
    ("Chronologie", "chronologie"),
    ("Notes", "notes"),
]

LEGACY_TYPE_MAP = {
    "person": EntityType.PERSON,
    "email": EntityType.EMAIL,
    "domain": EntityType.DOMAIN,
    "ip": EntityType.CUSTOM,
    "username": EntityType.USERNAME,
    "organization": EntityType.ORGANIZATION,
}


class DomainClient:
    async def _connect(self) -> aiosqlite.Connection:
        db = await aiosqlite.connect(_db_path())
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        return db

    @asynccontextmanager
    async def _session(self):
        db = await self._connect()
        try:
            yield db
        finally:
            await db.close()

    async def init_schema(self) -> None:
        db = await self._connect()
        try:
            await db.executescript(SCHEMA_SQL)
            await self._migrate_schema(db)
            await db.commit()
        finally:
            await db.close()
        logger.info("Domain schema initialized")

    async def _migrate_schema(self, db: aiosqlite.Connection) -> None:
        async with db.execute("PRAGMA table_info(dossiers)") as cur:
            cols = [row[1] for row in await cur.fetchall()]
        if "deleted_at" not in cols:
            await db.execute("ALTER TABLE dossiers ADD COLUMN deleted_at TEXT NULL")

    async def ensure_default_dossier(self) -> None:
        dossiers = await self.list_dossiers()
        if not dossiers:
            await self.create_dossier(DossierCreate(name="Investigation par défaut"), workspace_id="default")
        else:
            for d in dossiers:
                if d.workspace_id:
                    await self._migrate_workspace_blob(d.workspace_id, d.id)

    async def _migrate_workspace_blob(self, workspace_id: str, dossier_id: str) -> None:
        async with self._session() as db:
            async with db.execute(
                "SELECT COUNT(*) FROM entities WHERE dossier_id = ?", (dossier_id,)
            ) as cur:
                count = (await cur.fetchone())[0]
            if count > 0:
                return

        graph = await sqlite_client.load_graph(workspace_id)
        if not graph.get("nodes"):
            return

        carnets = await self.list_carnets(dossier_id)
        default_carnet = carnets[0].id if carnets else None
        node_id_map: dict[str, str] = {}

        for node in graph.get("nodes", []):
            etype = LEGACY_TYPE_MAP.get(node.get("type", "person"), EntityType.CUSTOM)
            entity = await self.create_entity(
                dossier_id,
                EntityCreate(entity_type=etype, label=node.get("label", "unknown"), carnet_id=default_carnet),
                actor="system",
            )
            node_id_map[node["id"]] = entity.id
            meta = node.get("metadata") or {}
            await self.add_observation(
                entity_id=entity.id,
                platform=meta.get("source", "import"),
                collection_method=CollectionMethod.IMPORT,
                content={"legacy_node_id": node["id"], "properties": node.get("properties", {})},
                confidence=float(meta.get("confidence", 50)) / 100.0,
            )

        for edge in graph.get("edges", []):
            src = node_id_map.get(edge.get("source"))
            tgt = node_id_map.get(edge.get("target"))
            if src and tgt:
                from models.domain import RelationType

                rtype = RelationType.LINKED_TO
                if edge.get("type") == "resolves_to":
                    rtype = RelationType.RESOLVES_TO
                elif edge.get("type") == "owns":
                    rtype = RelationType.OWNS
                elif edge.get("type") == "uses":
                    rtype = RelationType.USES
                await self.create_relation(
                    dossier_id,
                    RelationCreate(source_entity_id=src, target_entity_id=tgt, relation_type=rtype),
                    actor="system",
                )
        logger.info("Migrated workspace %s to dossier %s", workspace_id, dossier_id)

    async def create_dossier(
        self, data: DossierCreate, workspace_id: str | None = None, actor: str = "system"
    ) -> DossierOut:
        did = new_id()
        async with self._session() as db:
            await db.execute(
                """INSERT INTO dossiers (id, name, description, workspace_id)
                   VALUES (?, ?, ?, ?)""",
                (did, data.name, data.description, workspace_id),
            )
            for name, ntype in DEFAULT_CARNETS:
                await db.execute(
                    "INSERT INTO carnets (id, dossier_id, name, notebook_type) VALUES (?, ?, ?, ?)",
                    (new_id(), did, name, ntype),
                )
            await db.commit()
        await self.record_audit(actor, "DOSSIER_CREATED", "dossier", did, None, {"name": data.name})
        return await self.get_dossier(did)

    async def list_dossiers(self, include_deleted: bool = False) -> list[DossierOut]:
        query = "SELECT * FROM dossiers"
        if not include_deleted:
            query += " WHERE deleted_at IS NULL"
        query += " ORDER BY updated_at DESC"
        async with self._session() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query) as cur:
                rows = await cur.fetchall()
        result = []
        for row in rows:
            stats = await self._dossier_stats(row["id"])
            result.append(self._row_to_dossier(row, stats))
        return result

    def _row_to_dossier(self, row: aiosqlite.Row, stats: dict[str, int]) -> DossierOut:
        return DossierOut(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            workspace_id=row["workspace_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row["deleted_at"] if "deleted_at" in row.keys() else None,
            stats=stats,
        )

    async def list_deleted_dossiers(self) -> list[DossierOut]:
        async with self._session() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM dossiers WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC"
            ) as cur:
                rows = await cur.fetchall()
        result = []
        for row in rows:
            stats = await self._dossier_stats(row["id"])
            result.append(self._row_to_dossier(row, stats))
        return result

    async def soft_delete_dossier(self, dossier_id: str, actor: str = "system") -> DossierOut:
        dossier = await self.get_dossier(dossier_id)
        if dossier.deleted_at:
            return dossier
        async with self._session() as db:
            await db.execute(
                "UPDATE dossiers SET deleted_at = datetime('now'), updated_at = datetime('now') WHERE id = ?",
                (dossier_id,),
            )
            await db.commit()
        await self.record_audit(
            actor, "DOSSIER_DELETED", "dossier", dossier_id,
            {"name": dossier.name, "deleted_at": None},
            {"name": dossier.name, "deleted_at": "now"},
        )
        return await self.get_dossier(dossier_id, include_deleted=True)

    async def restore_dossier(self, dossier_id: str, actor: str = "system") -> DossierOut:
        dossier = await self.get_dossier(dossier_id, include_deleted=True)
        if not dossier.deleted_at:
            return dossier
        async with self._session() as db:
            await db.execute(
                "UPDATE dossiers SET deleted_at = NULL, updated_at = datetime('now') WHERE id = ?",
                (dossier_id,),
            )
            await db.commit()
        await self.record_audit(
            actor, "DOSSIER_RESTORED", "dossier", dossier_id,
            {"name": dossier.name, "deleted_at": dossier.deleted_at},
            {"name": dossier.name, "deleted_at": None},
        )
        return await self.get_dossier(dossier_id)

    async def permanent_delete_dossier(self, dossier_id: str, actor: str = "system") -> None:
        dossier = await self.get_dossier(dossier_id, include_deleted=True)
        async with self._session() as db:
            await db.execute("DELETE FROM dossiers WHERE id = ?", (dossier_id,))
            await db.commit()
        await self.record_audit(
            actor, "DOSSIER_PERMANENTLY_DELETED", "dossier", dossier_id,
            {"name": dossier.name},
            None,
        )

    async def _dossier_stats(self, dossier_id: str) -> dict[str, int]:
        async with self._session() as db:
            async with db.execute(
                "SELECT COUNT(*) FROM entities WHERE dossier_id = ? AND entity_type = 'PERSON'",
                (dossier_id,),
            ) as c:
                persons = (await c.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM entities WHERE dossier_id = ? AND entity_type IN ('SOCIAL_ACCOUNT','USERNAME')",
                (dossier_id,),
            ) as c:
                accounts = (await c.fetchone())[0]
            async with db.execute(
                "SELECT COUNT(*) FROM relations WHERE dossier_id = ?", (dossier_id,)
            ) as c:
                relations = (await c.fetchone())[0]
        return {"persons": persons, "accounts": accounts, "relations": relations}

    async def get_dossier(self, dossier_id: str, include_deleted: bool = False) -> DossierOut:
        async with self._session() as db:
            db.row_factory = aiosqlite.Row
            query = "SELECT * FROM dossiers WHERE id = ?"
            if not include_deleted:
                query += " AND deleted_at IS NULL"
            async with db.execute(query, (dossier_id,)) as cur:
                row = await cur.fetchone()
        if not row:
            raise ValueError("Dossier not found")
        return self._row_to_dossier(row, await self._dossier_stats(dossier_id))

    async def list_carnets(self, dossier_id: str) -> list[CarnetOut]:
        async with self._session() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT c.*, COUNT(e.id) as entity_count
                   FROM carnets c LEFT JOIN entities e ON e.carnet_id = c.id
                   WHERE c.dossier_id = ? GROUP BY c.id ORDER BY c.name""",
                (dossier_id,),
            ) as cur:
                rows = await cur.fetchall()
        return [
            CarnetOut(
                id=r["id"],
                dossier_id=r["dossier_id"],
                name=r["name"],
                notebook_type=r["notebook_type"],
                entity_count=r["entity_count"],
                created_at=r["created_at"],
            )
            for r in rows
        ]

    async def create_carnet(self, dossier_id: str, data: CarnetCreate, actor: str = "system") -> CarnetOut:
        cid = new_id()
        async with self._session() as db:
            await db.execute(
                "INSERT INTO carnets (id, dossier_id, name, notebook_type) VALUES (?, ?, ?, ?)",
                (cid, dossier_id, data.name, data.notebook_type.value),
            )
            await db.commit()
        await self.record_audit(actor, "CARNET_CREATED", "carnet", cid, None, {"name": data.name})
        carnets = await self.list_carnets(dossier_id)
        return next(c for c in carnets if c.id == cid)

    async def create_entity(
        self, dossier_id: str, data: EntityCreate, actor: str = "system"
    ) -> EntityOut:
        eid = new_id()
        async with self._session() as db:
            await db.execute(
                """INSERT INTO entities
                   (id, dossier_id, carnet_id, entity_type, label, properties, confidence, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    eid,
                    dossier_id,
                    data.carnet_id,
                    data.entity_type.value,
                    data.label,
                    json.dumps(data.properties),
                    data.confidence,
                    data.status.value,
                ),
            )
            await db.execute(
                "UPDATE dossiers SET updated_at = datetime('now') WHERE id = ?", (dossier_id,)
            )
            await db.commit()
        await self.add_observation(
            entity_id=eid,
            platform="manual",
            collection_method=CollectionMethod.MANUAL,
            content={"field": "label", "value": data.label},
            confidence=data.confidence,
            status=data.status,
        )
        note_content = data.properties.get("content")
        if isinstance(note_content, str) and note_content.strip():
            await self.add_observation(
                entity_id=eid,
                platform="manual",
                collection_method=CollectionMethod.MANUAL,
                content={"field": "notes", "value": note_content},
                confidence=data.confidence,
                status=data.status,
            )
        await self.record_audit(actor, "ENTITY_CREATED", "entity", eid, None, {"label": data.label})
        return await self.get_entity(eid)

    async def update_entity(
        self, entity_id: str, data: EntityUpdate, actor: str = "system"
    ) -> EntityOut:
        current = await self.get_entity(entity_id)
        updates: dict[str, Any] = {}
        if data.label is not None:
            updates["label"] = data.label
        if data.properties is not None:
            updates["properties"] = json.dumps(data.properties)
        if data.carnet_id is not None:
            updates["carnet_id"] = data.carnet_id
        if data.confidence is not None:
            updates["confidence"] = data.confidence
        if data.status is not None:
            updates["status"] = data.status.value
        if not updates:
            return current

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        params = list(updates.values()) + [entity_id]
        async with self._session() as db:
            await db.execute(
                f"UPDATE entities SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
                params,
            )
            await db.execute(
                "UPDATE dossiers SET updated_at = datetime('now') WHERE id = ?",
                (current.dossier_id,),
            )
            await db.commit()
        await self.record_audit(
            actor,
            "ENTITY_UPDATED",
            "entity",
            entity_id,
            {"label": current.label, "properties": current.properties},
            {
                "label": data.label if data.label is not None else current.label,
                "properties": data.properties if data.properties is not None else current.properties,
            },
        )
        return await self.get_entity(entity_id)

    async def delete_entity(self, entity_id: str, actor: str = "system") -> None:
        current = await self.get_entity(entity_id)
        async with self._session() as db:
            await db.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
            await db.execute(
                "UPDATE dossiers SET updated_at = datetime('now') WHERE id = ?",
                (current.dossier_id,),
            )
            await db.commit()
        await self.record_audit(
            actor,
            "ENTITY_DELETED",
            "entity",
            entity_id,
            {"label": current.label, "properties": current.properties},
            None,
        )

    async def get_entity(self, entity_id: str) -> EntityOut:
        async with self._session() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM entities WHERE id = ?", (entity_id,)) as cur:
                row = await cur.fetchone()
        if not row:
            raise ValueError("Entity not found")
        return EntityOut(
            id=row["id"],
            dossier_id=row["dossier_id"],
            carnet_id=row["carnet_id"],
            entity_type=row["entity_type"],
            label=row["label"],
            properties=json.loads(row["properties"] or "{}"),
            confidence=row["confidence"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def list_entities(
        self, dossier_id: str, carnet_id: str | None = None, entity_type: str | None = None
    ) -> list[EntityOut]:
        query = "SELECT * FROM entities WHERE dossier_id = ?"
        params: list[Any] = [dossier_id]
        if carnet_id:
            query += " AND carnet_id = ?"
            params.append(carnet_id)
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        query += " ORDER BY updated_at DESC"
        async with self._session() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cur:
                rows = await cur.fetchall()
        return [
            EntityOut(
                id=r["id"],
                dossier_id=r["dossier_id"],
                carnet_id=r["carnet_id"],
                entity_type=r["entity_type"],
                label=r["label"],
                properties=json.loads(r["properties"] or "{}"),
                confidence=r["confidence"],
                status=r["status"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in rows
        ]

    async def add_observation(
        self,
        entity_id: str,
        platform: str,
        collection_method: CollectionMethod,
        content: dict,
        confidence: float = 0.5,
        status: ConfidenceStatus = ConfidenceStatus.UNVERIFIED,
        url: str | None = None,
    ) -> str:
        sid = new_id()
        oid = new_id()
        async with self._session() as db:
            await db.execute(
                """INSERT INTO sources (id, entity_id, platform, url, collection_method)
                   VALUES (?, ?, ?, ?, ?)""",
                (sid, entity_id, platform, url, collection_method.value),
            )
            await db.execute(
                """INSERT INTO observations (id, source_id, entity_id, content, confidence, status)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (oid, sid, entity_id, json.dumps(content), confidence, status.value),
            )
            await db.commit()
        return oid

    async def create_relation(
        self, dossier_id: str, data: RelationCreate, actor: str = "system"
    ) -> RelationOut:
        rid = new_id()
        async with self._session() as db:
            await db.execute(
                """INSERT INTO relations
                   (id, dossier_id, source_entity_id, target_entity_id, relation_type, confidence, status, evidence_ids)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rid,
                    dossier_id,
                    data.source_entity_id,
                    data.target_entity_id,
                    data.relation_type.value,
                    data.confidence,
                    data.status.value,
                    json.dumps(data.evidence_ids),
                ),
            )
            await db.commit()
        await self.record_audit(actor, "RELATION_CREATED", "relation", rid, None, data.model_dump())
        return await self.get_relation(rid)

    async def get_relation(self, relation_id: str) -> RelationOut:
        async with self._session() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM relations WHERE id = ?", (relation_id,)) as cur:
                row = await cur.fetchone()
        if not row:
            raise ValueError("Relation not found")
        return RelationOut(
            id=row["id"],
            dossier_id=row["dossier_id"],
            source_entity_id=row["source_entity_id"],
            target_entity_id=row["target_entity_id"],
            relation_type=row["relation_type"],
            confidence=row["confidence"],
            status=row["status"],
            evidence_ids=json.loads(row["evidence_ids"] or "[]"),
            created_at=row["created_at"],
        )

    async def list_relations(self, dossier_id: str, entity_id: str | None = None) -> list[RelationOut]:
        query = "SELECT * FROM relations WHERE dossier_id = ?"
        params: list[Any] = [dossier_id]
        if entity_id:
            query += " AND (source_entity_id = ? OR target_entity_id = ?)"
            params.extend([entity_id, entity_id])
        async with self._session() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cur:
                rows = await cur.fetchall()
        return [
            RelationOut(
                id=r["id"],
                dossier_id=r["dossier_id"],
                source_entity_id=r["source_entity_id"],
                target_entity_id=r["target_entity_id"],
                relation_type=r["relation_type"],
                confidence=r["confidence"],
                status=r["status"],
                evidence_ids=json.loads(r["evidence_ids"] or "[]"),
                created_at=r["created_at"],
            )
            for r in rows
        ]

    async def get_observations_for_entity(self, entity_id: str) -> list[dict]:
        async with self._session() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT o.*, s.platform, s.collection_method, s.url, s.collected_at
                   FROM observations o JOIN sources s ON s.id = o.source_id
                   WHERE o.entity_id = ? ORDER BY o.observed_at DESC""",
                (entity_id,),
            ) as cur:
                rows = await cur.fetchall()
        return [
            {
                "id": r["id"],
                "content": json.loads(r["content"]),
                "confidence": r["confidence"],
                "status": r["status"],
                "observed_at": r["observed_at"],
                "platform": r["platform"],
                "collection_method": r["collection_method"],
                "url": r["url"],
                "collected_at": r["collected_at"],
            }
            for r in rows
        ]

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        q = query.strip().lower()
        if not q:
            return []
        async with self._session() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """SELECT e.*, d.name as dossier_name FROM entities e
                   JOIN dossiers d ON d.id = e.dossier_id
                   WHERE d.deleted_at IS NULL
                     AND (lower(e.label) LIKE ? OR lower(e.properties) LIKE ?)
                   LIMIT ?""",
                (f"%{q}%", f"%{q}%", limit),
            ) as cur:
                rows = await cur.fetchall()
        results = []
        for r in rows:
            label_lower = r["label"].lower()
            if label_lower == q:
                match_type = "exact"
            elif q in label_lower:
                match_type = "normalized"
            else:
                match_type = "potential"
            results.append(
                {
                    "id": r["id"],
                    "label": r["label"],
                    "entity_type": r["entity_type"],
                    "dossier_id": r["dossier_id"],
                    "dossier_name": r["dossier_name"],
                    "match_type": match_type,
                }
            )
        return results

    async def record_audit(
        self,
        actor: str,
        action: str,
        entity_type: str,
        entity_id: str,
        previous_state: dict | None,
        new_state: dict | None,
    ) -> None:
        async with self._session() as db:
            await db.execute(
                """INSERT INTO audit_events (id, actor, action, entity_type, entity_id, previous_state, new_state)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    new_id(),
                    actor,
                    action,
                    entity_type,
                    entity_id,
                    json.dumps(previous_state) if previous_state else None,
                    json.dumps(new_state) if new_state else None,
                ),
            )
            await db.commit()

    async def list_audit_events(self, entity_id: str | None = None, limit: int = 50) -> list[dict]:
        query = "SELECT * FROM audit_events"
        params: list[Any] = []
        if entity_id:
            query += " WHERE entity_id = ?"
            params.append(entity_id)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        async with self._session() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cur:
                rows = await cur.fetchall()
        return [
            {
                "id": r["id"],
                "actor": r["actor"],
                "action": r["action"],
                "entity_type": r["entity_type"],
                "entity_id": r["entity_id"],
                "previous_state": json.loads(r["previous_state"]) if r["previous_state"] else None,
                "new_state": json.loads(r["new_state"]) if r["new_state"] else None,
                "timestamp": r["timestamp"],
            }
            for r in rows
        ]


domain_client = DomainClient()
