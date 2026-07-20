# Stack Technique OSINTGraph

## Frontend

- TypeScript, React 18, Vite
- Zustand (`graphStore.ts`, `investigationStore.ts`)
- Cytoscape.js (`cytoscape-cola`, `cytoscape-dagre`)
- CSS natif + variables (`index.css`), thème **Matte & Vintage**
- React Router pour Investigation Workspace

## Cloud (Streamlit)

- Entry : `streamlit_app.py` (racine)
- Vues : package `ui/` (imports directs backend, pas HTTP)
- Dépendances cloud : `requirements.txt` (racine)
- Secrets : `.streamlit/secrets.toml` (local) ou Streamlit Cloud admin
- **Ne pas renommer** `ui/` en `streamlit/` (conflit avec le package pip)

## Desktop

- Electron, `nodeIntegration: false`, `contextIsolation: true`
- Preload : `window.osint.api`

## Backend

- Python 3.11+, FastAPI, uvicorn
- Entrypoint dev : `main:asgi_app` (Socket.IO + FastAPI)
- Socket.IO via `python-socketio`
- SQLite : blob legacy + schéma relationnel (`domain_client`)
- Transforms : plugins dans `transforms/`

### Planifié (non implémenté)

- Neo4j client
- Agent-OS (`agent_os.py`, `agents/`)
- Celery + Redis

## Conventions

- **TypeScript** : `camelCase`, interfaces `PascalCase`, éviter `any`
- **Python** : PEP8, `snake_case`, type hints obligatoires
- **Commentaires** : blocs complexes uniquement

## Variables d'environnement

Voir `backend/.env.example` :

- `CORS_ORIGINS`, `SHODAN_API_KEY`, `HIBP_API_KEY`
- `SQLITE_PATH` (défaut: `osintgraph.db` ; recommandé local : `data/osintgraph.db`)
- `OSINTGRAPH_SESSION_SECRET` (auth locale)
- `AI_PROVIDER`, `AI_API_KEY` *(optionnel, pour analyse IA)*

## Neo4j *(planifié)*

Variables `NEO4J_*` dans `.env.example` pour usage futur. Non requis en v1.
