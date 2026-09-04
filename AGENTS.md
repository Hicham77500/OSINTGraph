# OSINTGraph — Guide agents

> Point d'entrée pour tout agent IA travaillant sur ce dépôt.

## Vision

OSINTGraph est une plateforme d'investigation OSINT orientée **analyse relationnelle**. Elle organise des recherches sur personnes, pseudonymes, organisations, comptes publics et présences numériques — **uniquement** à partir de sources ouvertes, de données fournies volontairement par l'analyste ou de méthodes légalement accessibles.

## Stack (état juillet 2026)

- **Frontend (référence)** : React 18, TypeScript, Vite, Zustand, Cytoscape, Electron — thème Matte & Vintage
- **Cloud (optionnel)** : Streamlit (`streamlit_app.py` + `ui/`) sur Streamlit Community Cloud
- **Backend** : FastAPI, Python 3.11+, SQLite (relationnel + blob legacy)
- **Realtime** : Socket.IO (entrypoint `main:asgi_app`)
- **OSINT** : plugins `backend/plugins/` + connecteurs `connectors/` (extensible)

**Planifié, non implémenté** : Neo4j, Agent-OS orchestrateur, Celery.

## Architecture

```
frontend/src/           UI principale (React + Cytoscape) — NE PAS SUPPRIMER
  pages/                Investigation Workspace, Person View
  graph/                Cytoscape + graphStore
  components/           Layout, panels, modals, search
  services/             api.ts, websocket.ts

streamlit_app.py        Entry point déploiement cloud
ui/                     Vues Streamlit (dossiers, graphe, carnets…) — cloud uniquement
  services/backend.py   Imports directs backend (sans HTTP)

backend/
  routers/              REST legacy + api/v1/
  plugins/              Transforms OSINT (plugin.json + plugin.py)
  connectors/           PlatformConnector
  db/                   sqlite_client (legacy) + domain_client (relationnel)
  models/               Pydantic domain models
  services/             entity_resolution, context_readiness, audit
  middleware/           auth, rate_limit

deploy/
  docker.md             Déploiement Docker (React + API + SpiderFoot optionnel)
  streamlit-cloud.md    Guide déploiement cloud
docs/
  GETTING_STARTED.md    Guide utilisateur (modes, setup, fork)
  PROJECT_CONTEXT.md    UX investigation, carnets, routing
  DEATH_SEARCH.md       Recherche décès INSEE
CONTRIBUTING.md         Fork workflow, conventions PR
requirements.txt        Dépendances Streamlit Cloud (racine)
scripts/                setup.ps1 / setup.sh
```

## Hiérarchie métier

```
Dossier → Carnet → Entité → Source → Observation → Evidence → Relation → Hypothesis
```

Voir `.agent/specs/001-domain-model.md` pour le modèle complet.

## Interdits absolus

Ne jamais implémenter :

- contournement d'authentification
- accès à des comptes privés
- vol de session, credential stuffing
- bypass de protections plateforme
- stalking automatisé
- deanonymisation présentée comme certaine sans preuves publiques

Une hypothèse IA n'est **jamais** un fait. Toujours conserver provenance et niveau d'incertitude.

## Conventions

| Zone | Règle |
|------|-------|
| État frontend | Zustand ; pas de Redux |
| Graphe | Cytoscape + `NODE_TYPE_CONFIG` |
| UI React | Thème Matte & Vintage, CSS variables, Cytoscape |
| UI Streamlit (`ui/`) | Cloud uniquement ; package `ui/` (pas `streamlit/` — conflit de module) |
| Electron | `contextIsolation: true`, pas de `nodeIntegration` |
| Backend Python | PEP8, type hints, `snake_case` |
| TypeScript | `camelCase`, éviter `any` |
| Transforms | 1 fichier = 1 plugin ; provenance obligatoire dans le retour |
| i18n | `en.ts` + `fr.ts` pour tout texte UI |

## Ordre d'exécution recommandé

1. Lire `.agent/standards/` et cette page
2. Inspecter l'existant avant modification
3. Réutiliser composants et patterns existants
4. Modifications limitées, testables, compatibles
5. Documenter décisions dans `.agent/specs/` si impact architectural

## Fichiers de contexte

| Fichier | Rôle |
|---------|------|
| `docs/PROJECT_CONTEXT.md` | UX investigation, carnets, routing map |
| `docs/DEATH_SEARCH.md` | Recherche décès INSEE, config Parquet, demande d'actes |
| `.cursor/rules/osintgraph-core.mdc` | Stack, architecture, conventions |
| `.cursor/rules/investigation-ethics.mdc` | Limites légales et éthiques |
| `.cursor/rules/backend-python.mdc` | Conventions backend |
| `.cursor/rules/frontend-react.mdc` | Conventions frontend React |
| `.cursor/rules/streamlit-ui.mdc` | Conventions UI cloud Streamlit |
| `.cursor/skills/` | Skills projet (transforms, provenance, éthique) |
| `docs/AUDIT-2026-07.md` | Diagnostic initial |

## Routing (frontend)

| Route | Vue | Usage |
|-------|-----|-------|
| `/` | Dossiers | Liste des investigations |
| `/trash` | TrashPage | Corbeille — dossiers supprimés (restauration / suppression définitive) |
| `/dossier/:id` | Dossier | Grille des carnets |
| `/dossier/:id/carnet/:cid` | CarnetViewPage | Liste / chronologie / notes selon `notebook_type` |
| `/dossier/:id/graph` | CarnetGraphPage | Graphe legacy Cytoscape |
| `/dossier/:id/person/:eid` | PersonViewPage | Fiche personne (+ recherche décès INSEE) |

Détails : [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md).  
Recherche décès : [`docs/DEATH_SEARCH.md`](docs/DEATH_SEARCH.md).

## Tests

```bash
# Backend
cd backend && .venv/bin/pytest

# Frontend
cd frontend && npm test
```

## Déploiement

| Mode | Commande | UI |
|------|----------|-----|
| **Local (complet)** | `npm run dev` | React Matte & Vintage + Cytoscape |
| **Docker (prod)** | `docker compose up --build` | React nginx :8080 + API :8000 |
| **Cloud** | Streamlit Cloud → `streamlit_app.py` | Streamlit (`ui/`) |
| **Preview cloud local** | `npm run dev:streamlit` | Streamlit |

Guides : [`deploy/docker.md`](deploy/docker.md) · [`deploy/streamlit-cloud.md`](deploy/streamlit-cloud.md) · [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md)

## Fork / contribution

Les contributeurs travaillent depuis un **fork GitHub** — voir [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Démarrage dev

```bash
./scripts/setup.sh       # ou .\scripts\setup.ps1 (Windows)
npm run dev              # React + API (UI complète)
npm run dev:streamlit    # Preview déploiement Streamlit
```
