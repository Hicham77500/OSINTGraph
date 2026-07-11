# OSINTGraph — Guide agents

> Point d'entrée pour tout agent IA travaillant sur ce dépôt.

## Vision

OSINTGraph est une plateforme d'investigation OSINT orientée **analyse relationnelle**. Elle organise des recherches sur personnes, pseudonymes, organisations, comptes publics et présences numériques — **uniquement** à partir de sources ouvertes, de données fournies volontairement par l'analyste ou de méthodes légalement accessibles.

## Stack (état juillet 2026)

- **Frontend** : React 18, TypeScript, Vite, Zustand, Cytoscape, Electron
- **Backend** : FastAPI, Python 3.11+, SQLite (relationnel + blob legacy)
- **Realtime** : Socket.IO (entrypoint `main:asgi_app`)
- **OSINT** : plugins `transforms/` + connecteurs `connectors/` (extensible)

**Planifié, non implémenté** : Neo4j, Agent-OS orchestrateur, Celery.

## Architecture

```
frontend/src/
  pages/          Investigation Workspace, Person View
  graph/          Cytoscape + graphStore
  components/     Layout, panels, modals, search
  services/       api.ts, websocket.ts
  types/          Modèles domaine partagés

backend/
  routers/        REST legacy + api/v1/
  transforms/     Plugins OSINT (@register)
  connectors/     PlatformConnector (MANUAL, PUBLIC_SEARCH, OFFICIAL_API, IMPORT)
  db/             sqlite_client (legacy) + domain_client (relationnel)
  models/         Pydantic domain models
  services/       entity_resolution, context_readiness, audit
  middleware/     auth, rate_limit
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
| UI | Dark Glassmorphism, CSS variables |
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
| `.cursor/rules/osintgraph-core.mdc` | Stack, architecture, conventions |
| `.cursor/rules/investigation-ethics.mdc` | Limites légales et éthiques |
| `.cursor/rules/backend-python.mdc` | Conventions backend |
| `.cursor/rules/frontend-react.mdc` | Conventions frontend |
| `.cursor/skills/` | Skills projet (transforms, provenance, éthique) |
| `docs/AUDIT-2026-07.md` | Diagnostic initial |

## Routing (frontend)

| Route | Vue | Usage |
|-------|-----|-------|
| `/` | Dossiers | Liste des investigations |
| `/dossier/:id` | Dossier | Grille des carnets |
| `/dossier/:id/carnet/:cid` | CarnetViewPage | Liste / chronologie / notes selon `notebook_type` |
| `/dossier/:id/graph` | CarnetGraphPage | Graphe legacy Cytoscape |
| `/dossier/:id/person/:eid` | PersonViewPage | Fiche personne |

Détails : [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md).

## Tests

```bash
# Backend
cd backend && .venv/bin/pytest

# Frontend
cd frontend && npm test
```

## Démarrage dev

```bash
npm run dev   # backend (asgi_app) + frontend Vite
```
