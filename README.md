# OSINTGraph

> Plateforme OSINT / Graph Intelligence — Maltego-inspired

**FR** — OSINTGraph organise vos investigations en **dossiers** et **carnets**, relie personnes, comptes et artefacts dans un **graphe relationnel**, et trace chaque fait avec **provenance** et niveaux de confiance. Sources ouvertes et données fournies par l'analyste uniquement.

**EN** — OSINTGraph structures investigations into **dossiers** and **carnets**, links people, accounts, and artifacts in a **relational graph**, and tracks every datum with **provenance** and confidence levels. Open sources and analyst-provided data only.

## Fonctionnalités

| Module | Description |
|--------|-------------|
| **Dossiers** | Investigations isolées avec statistiques |
| **Carnets** | Notes, chronologie, listes typées |
| **Graphe** | Visualisation interactive (PyVis), transforms OSINT |
| **Provenance** | Source, observation, confiance (CONFIRMED → CONTRADICTED) |
| **Import / Export** | JSON, CSV, Markdown |
| **Corbeille** | Restauration ou suppression définitive |
| **Recherche** | Recherche globale cross-dossiers |

## Stack

- **UI** : Streamlit (Python)
- **Backend** : FastAPI + Python 3.11 + asyncio + SQLite (import direct)
- **Graphe** : PyVis (visualisation interactive)
- **OSINT** : plugins `backend/plugins/` (Sherlock, Shodan, etc.)

*Planifié : Neo4j, Agent-OS orchestrator*

## Quickstart local

### Prérequis

- Python 3.11+

### Installation

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp backend/.env.example backend/.env   # optionnel — clés API
streamlit run streamlit_app.py
```

→ http://localhost:8501

### Données de démo

```bash
cd backend && python scripts/seed_test_dossier.py
```

## Déploiement Streamlit Cloud

1. Pousser le dépôt sur GitHub
2. [share.streamlit.io](https://share.streamlit.io) → New app
3. **Main file** : `streamlit_app.py`
4. **Requirements** : `requirements.txt` (racine)
5. Secrets (optionnel) : `SHODAN_API_KEY`, `HIBP_API_KEY`, `SQLITE_PATH`

> La base SQLite est éphémère sur Streamlit Cloud (redémarrage = reset). Pour la persistance, monter un volume ou utiliser un hébergement self-hosted.

## Architecture

```
OSINTGraph/
  streamlit_app.py        Point d'entrée Streamlit
  ui/
    services/             Bridge backend (domain_client, plugins)
    views/                Pages UI (dossiers, graphe, carnets, person)
  backend/                Moteur FastAPI + domaine + plugins OSINT
    routers/              API REST (legacy, optionnel)
    plugins/              Transforms OSINT
    db/                   SQLite (relationnel + blob graphe)
    services/             Entity resolution, AI readiness, audit
  data/                   Base SQLite locale (gitignored)
```

**Contexte** — [`AGENTS.md`](AGENTS.md) · [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md)

## Built-in Transforms

| Transform | Input | Output |
|-----------|-------|--------|
| DNS Lookup | Domain | IP |
| Whois Lookup | Domain | Organization |
| HIBP Lookup | Email | Domain (breach) |
| Shodan Lookup | IP, Domain | Organization, Location, Port |
| Sherlock Lookup | Username | Social Account |
| IP Geolocation | IP | Location |
| Phone Lookup | Phone | Location |
| Holehe Lookup | Email | Username |

## Tests

```bash
cd backend && .venv/bin/pytest
```

## Agent context

See [`AGENTS.md`](AGENTS.md) for AI agent guidelines.
