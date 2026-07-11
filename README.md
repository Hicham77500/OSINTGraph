# OSINTGraph

> Desktop OSINT / Graph Intelligence Application — Maltego-inspired

## Stack

- **Frontend**: Electron + React 18 + TypeScript + Vite + Cytoscape.js
- **Backend**: FastAPI + Python 3.11 + asyncio + SQLite
- **Realtime**: Socket.IO (via `main:asgi_app`)
- **Domain API**: `/api/v1/` (dossiers, carnets, entités, provenance)

*Planifié : Neo4j, Agent-OS orchestrator*

## Quickstart

### Prerequisites

- Node.js 20+
- Python 3.11+

### All-in-one (recommended)

```bash
npm install
cd backend && python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
cp .env.example .env
cd .. && npm run dev
```

- Frontend: http://localhost:5173/
- Backend: http://127.0.0.1:8000
- Health: http://127.0.0.1:8000/health

### Electron desktop

```bash
cd frontend && npm run electron:dev
```

## Architecture

```
OSINTGraph/
  frontend/           Electron + React UI
    src/pages/        Investigation Workspace
    src/graph/        Cytoscape + stores
    src/components/   Layout, panels, search
    src/services/     API + WebSocket
  backend/            FastAPI server
    routers/          Legacy + api/v1
    transforms/       OSINT plugins
    connectors/       Platform connectors
    db/               SQLite (legacy blob + domain)
    services/         Entity resolution, AI readiness, audit
  .agent/standards/   Conventions projet
  .cursor/rules/      Règles Cursor
  docs/               Documentation
```

## Entity Types (legacy graph)

`Person` · `Email` · `Domain` · `IP` · `Username` · `Organization`

Domain model (v1): see `.agent/specs/001-domain-model.md`

## Built-in Transforms

| Transform | Input | Output |
|-----------|-------|--------|
| DNS Lookup | Domain | IP |
| Whois Lookup | Domain | Organization |
| HIBP Lookup | Email | Domain (breach) |
| Shodan Lookup | IP | Organization |
| Sherlock Lookup | Username | Username |
| Holehe Lookup | Email | Username |

## Agent context

See [`AGENTS.md`](AGENTS.md) for AI agent guidelines.

## Tests

```bash
cd backend && .venv/bin/pytest
cd frontend && npm test
```

## Security audit

```bash
cd backend && .venv/bin/pip-audit
npm audit
```
