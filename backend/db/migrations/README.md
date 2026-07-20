# Schema migrations

OSINTGraph uses **inline migrations** in `domain_client._migrate_schema()` rather than versioned SQL files.

## Why

- Single SQLite file (local : `data/osintgraph.db` ou `SQLITE_PATH` ; Streamlit Cloud : éphémère)
- Small, additive changes (e.g. `ALTER TABLE … ADD COLUMN`)
- `init_schema()` runs on every startup via FastAPI lifespan

## Adding a migration

1. Edit `_migrate_schema()` in `domain_client.py`
2. Check column/table existence with `PRAGMA table_info` before `ALTER`
3. Keep changes idempotent (`IF NOT EXISTS` / guard checks)
4. Document the change in this folder if non-trivial

## Example (existing)

```python
async def _migrate_schema(self, db: aiosqlite.Connection) -> None:
    async with db.execute("PRAGMA table_info(dossiers)") as cur:
        cols = [row[1] for row in await cur.fetchall()]
    if "deleted_at" not in cols:
        await db.execute("ALTER TABLE dossiers ADD COLUMN deleted_at TEXT NULL")
```

Postgres or Alembic-style migrations are **out of scope** until a future phase.
