# OSINTGraph — Persistence (SQLite)

Single SQLite file, dual persistence layers. Path controlled by `SQLITE_PATH` (default `osintgraph.db`; local Streamlit: `data/osintgraph.db`).

## Layers

| Layer | Module | Tables | Role |
|-------|--------|--------|------|
| **Domain (relational)** | `domain_client.py` | `dossiers`, `carnets`, `entities`, `sources`, `observations`, `relations`, `evidence`, `hypotheses`, `merge_suggestions`, `audit_events` | Canonical investigation model (v1 API) |
| **Graph blob (legacy)** | `sqlite_client.py` | `graphs` | Cytoscape JSON per `workspace_id`; dual-write during migration |

Both clients read `SQLITE_PATH` and share the **same file**. WAL mode and foreign keys are enabled on every connection.

## Startup

`main.py` lifespan:

1. Creates parent directory of `SQLITE_PATH` if missing
2. `domain_client.init_schema()` — `CREATE TABLE IF NOT EXISTS` + inline migrations
3. `domain_client.ensure_default_dossier()` — default dossier + blob→entity migration when needed

## Schema migrations

Incremental changes live in `domain_client._migrate_schema()` (not separate SQL files). See `migrations/README.md` for the convention.

## Backup

Copy the database file when the app is not writing:

```bash
cp data/osintgraph.db data/osintgraph.db.bak
```

WAL mode may produce companion files (`-wal`, `-shm`). For a consistent backup, stop the app first or use SQLite `.backup`.
