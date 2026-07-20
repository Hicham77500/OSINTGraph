# OSINTGraph — Guide agents

> Point d'entrée pour tout agent IA travaillant sur ce dépôt.

## Vision

OSINTGraph est une plateforme d'investigation OSINT orientée **analyse relationnelle**. Elle organise des recherches sur personnes, pseudonymes, organisations, comptes publics et présences numériques — **uniquement** à partir de sources ouvertes, de données fournies volontairement par l'analyste ou de méthodes légalement accessibles.

## Stack (état juillet 2026)

- **UI** : Streamlit (Python) — `streamlit_app.py` + `streamlit/views/`
- **Backend** : FastAPI, Python 3.11+, SQLite (relationnel + blob legacy)
- **Graphe** : PyVis (visualisation dans Streamlit)
- **OSINT** : plugins `backend/plugins/` + connecteurs `connectors/`

**Planifié, non implémenté** : Neo4j, Agent-OS orchestrateur, Celery.

## Architecture

```
streamlit_app.py          Point d'entrée UI
streamlit/
  services/backend.py     Bridge direct vers domain_client, plugins
  views/                  dossiers, carnet, graph, person, trash

backend/
  routers/                REST legacy + api/v1/ (optionnel, tests)
  plugins/                Transforms OSINT (plugin.json + plugin.py)
  connectors/             PlatformConnector
  db/                     sqlite_client (legacy) + domain_client (relationnel)
  models/                 Pydantic domain models
  services/               entity_resolution, context_readiness, audit
  middleware/             auth, rate_limit
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
| UI | Streamlit ; navigation via `st.session_state.page` |
| Graphe | PyVis + sauvegarde via `sqlite_client` |
| Backend Python | PEP8, type hints, `snake_case` |
| Transforms | 1 plugin = 1 dossier avec `plugin.json` ; provenance obligatoire |
| Texte UI | Français par défaut dans les vues Streamlit |

## Navigation UI (Streamlit)

| `session_state.page` | Vue |
|----------------------|-----|
| `dossiers` | Liste des investigations |
| `trash` | Corbeille |
| `dossier` | Hub carnets |
| `carnet` | Entités / notes / chronologie |
| `graph` | Graphe + transforms |
| `person` | Fiche entité |

## Ordre d'exécution recommandé

1. Lire `.agent/standards/` et cette page
2. Inspecter l'existant avant modification
3. Modifications limitées, testables, compatibles
4. Documenter décisions dans `.agent/specs/` si impact architectural

## Fichiers de contexte

| Fichier | Rôle |
|---------|------|
| `docs/PROJECT_CONTEXT.md` | UX investigation, carnets |
| `.cursor/rules/osintgraph-core.mdc` | Stack, architecture |
| `.cursor/rules/investigation-ethics.mdc` | Limites légales |
| `.cursor/rules/backend-python.mdc` | Conventions backend |

## Démarrage dev

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Tests

```bash
cd backend && .venv/bin/pytest
```
