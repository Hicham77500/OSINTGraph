# Architecture OSINTGraph

> État réel — juillet 2026. Sections marquées *(planifié)* ne sont pas encore implémentées.

## Vue d'ensemble

OSINTGraph est une application desktop modulaire :

1. **Frontend (React + Vite)** — UI, graphe Cytoscape, Investigation Workspace
2. **Electron** — conteneur natif, `contextBridge` strict (`window.osint.api`)
3. **Backend (FastAPI)** — API REST, transforms OSINT, persistance SQLite

## 1. Frontend

- **État global** : Zustand (`graphStore`, `investigationStore`). Pas de Redux.
- **État UI** : actuellement dans `graphStore` (layout, connectMode). Split optionnel futur.
- **Graphe** : Cytoscape.js, layouts `cola` / `dagre`, styles via `NODE_TYPE_CONFIG`
- **UI** : thème Matte & Vintage, CSS variables (`index.css`)
- **Routing** : React Router — dossiers → carnets grid → carnet view / person view / full graph

Voir `docs/PROJECT_CONTEXT.md` pour la carte des routes et le rôle de chaque carnet.

## 2. Backend

- `routers/` — endpoints legacy (`/graph`, `/transforms`, `/workspaces`) + `/api/v1/`
- `plugins/` — transforms OSINT (production, `plugin.json` + auto-discovery)
- `transforms/` — legacy (`@register`), migration vers `plugins/`
- `connectors/` — PlatformConnector *(extensible)*
- `db/` — `sqlite_client` (blob legacy) + `domain_client` (relationnel)
- `services/` — entity_resolution, context_readiness, audit
- `middleware/` — auth locale, rate limiting

### *(Planifié)* Agent-OS

Orchestration de pipelines transforms. Non implémenté. Transforms exécutés via REST.

### *(Planifié)* Neo4j

Graph DB optionnelle pour très grands graphes. SQLite relationnel utilisé en v1.

## 3. Temps réel

Socket.IO monté via `main:asgi_app`. Events :

- `transform:start`
- `transform:result`
- `transform:error`

Frontend peut s'abonner via `services/websocket.ts`.

## 4. Persistance

- **Legacy** : table `graphs(workspace_id, data JSON)`
- **Domaine** : tables relationnelles (dossiers, carnets, entities, sources, observations, evidence, relations, hypotheses, audit_events)
- **Migration** : dual-write ; `workspace_id` = alias `dossier_id`

## 5. Communication

- REST localhost:8000 (config + CRUD)
- Socket.IO pour progression transforms
- Electron IPC proxy vers backend

## 6. Sécurité Electron

`nodeIntegration: false`, `contextIsolation: true`, preload obligatoire.

## 7. Déploiement

| Mode | Commande / cible | UI |
|------|------------------|-----|
| Dev local | `npm run dev` | React + Cytoscape (référence) |
| Docker prod | `docker compose up --build` | React nginx :8080 + API :8000 |
| Cloud | Streamlit Community Cloud → `streamlit_app.py` | Streamlit (`ui/`) |
| Preview cloud | `npm run dev:streamlit` | Streamlit local |

- Guides : `deploy/docker.md`, `deploy/streamlit-cloud.md`, `docs/GETTING_STARTED.md`
- Docker et Streamlit Cloud coexistent : Docker pour React en production ; Streamlit pour accès cloud léger
- L'UI React dans `frontend/` reste la référence visuelle complète
