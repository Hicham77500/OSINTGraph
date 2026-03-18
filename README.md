# OSINTGraph

> Desktop OSINT / Graph Intelligence Application — Maltego-inspired

## Stack
- **Frontend**: Electron + React 18 + TypeScript + Vite + Cytoscape.js
- **Backend**: FastAPI + Python 3.11 + asyncio
- **Graph DB**: Neo4j (primary) · SQLite (fallback)
- **Realtime**: Socket.IO / WebSocket
- **Orchestration**: Agent-OS

## Quickstart

### Prerequisites
- Node.js 20+
- Python 3.11+
- (Optional) Neo4j 5+

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env     # Fill your API keys
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # Vite dev server (browser)
npm run electron:dev # Electron desktop app
```

## Architecture
```
OsintGraph/
  frontend/           Electron + React UI
    electron/         Main + Preload scripts
    src/
      graph/          Cytoscape engine + stores
      components/     Layout, panels, modals
      services/       API + WebSocket clients
  backend/            FastAPI server
    routers/          REST endpoints
    transforms/       OSINT transform plugins
    agents/           Agent-OS orchestrator
    db/               Neo4j + SQLite clients
  agent-os/           Pipeline config
```

## Entity Types
`Person` · `Email` · `Domain` · `IP` · `Username` · `Organization`

## Built-in Transforms
| Transform | Input | Output |
|-----------|-------|--------|
| DNS Lookup | Domain | IP |
| Whois Lookup | Domain | Person / Org |
| HIBP Lookup | Email | Breach data |
| Shodan Lookup | IP | Services / Ports |
