# OSINTGraph — Persistence (SQLite)

Single SQLite file, dual persistence layers. Path controlled by `SQLITE_PATH` (default `osintgraph.db`; Docker: `/data/osintgraph.db`).

## Layers

| Layer | Module | Tables | Role |
|-------|--------|--------|------|
| **Domain (relational)** | `domain_client.py` | `dossiers`, `carnets`, `entities`, `sources`, `observations`, `relations`, `evidence`, `hypotheses`, `merge_suggestions`, `audit_events` | Canonical investigation model (v1 API) |
| **Graph blob (legacy)** | `sqlite_client.py` | `graphs` | Cytoscape JSON per `workspace_id`; dual-write during migration |

Both clients read `SQLITE_PATH` and share the **same file**. WAL mode and foreign keys are enabled on every connection.

## Startup

`main.py` lifespan:

1. Creates parent directory of `SQLITE_PATH` if missing (Docker volume `/data`)
2. `domain_client.init_schema()` — `CREATE TABLE IF NOT EXISTS` + inline migrations
3. `domain_client.ensure_default_dossier()` — default dossier + blob→entity migration when needed

## Schema migrations

Incremental changes live in `domain_client._migrate_schema()` (not separate SQL files). See `migrations/README.md` for the convention.

## Backup

Stop containers (or ensure no writes), then copy the database file:

```bash
docker compose exec api cp /data/osintgraph.db /data/osintgraph.db.bak
# or copy the named volume from the host
```

WAL mode may produce companion files (`-wal`, `-shm`). For a consistent backup, stop the `api` service first or use SQLite `.backup`.

## Docker volume

`docker-compose.yml` mounts `osintgraph_data` at `/data`. All investigation data persists across image rebuilds.
