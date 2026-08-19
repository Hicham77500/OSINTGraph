# OSINTGraph

> Desktop OSINT / Graph Intelligence Application — Maltego-inspired

**FR** — OSINTGraph organise vos investigations en **dossiers** et **carnets**, relie personnes, comptes et artefacts dans un **graphe relationnel**, et trace chaque fait avec **provenance** et niveaux de confiance. Sources ouvertes et données fournies par l'analyste uniquement.

**EN** — OSINTGraph structures investigations into **dossiers** and **carnets**, links people, accounts, and artifacts in a **relational graph**, and tracks every datum with **provenance** and confidence levels. Open sources and analyst-provided data only.

## Nouveautés (Mise à jour v2.0 - Juillet 2026)

- 🔌 **Architecture Plugins Dynamiques** : Les "transforms" (Shodan, Sherlock, etc.) sont désormais de véritables plugins découpés avec des manifestes `plugin.json` permettant une auto-découverte.
- 🧬 **Registres d'entités dynamiques** : Le typage du graphe est désormais extensible. Nouveaux types ajoutés : `PHONE`, `LOCATION`, `SOCIAL_ACCOUNT`.
- 🔑 **API Manager** : Un système intégré gère désormais les clés et quotas d'API des différents fournisseurs de façon centralisée.
- 🎨 **Refonte graphique** : Nouvelle interface "Matte & Vintage" professionnelle, éliminant le surplus de *glassmorphism* pour une meilleure lisibilité. Typographie IBM Plex Mono pour les données techniques.
- 💾 **Sauvegarde automatique** : Vos graphes et investigations sont désormais sauvegardés en temps réel sans action requise.

## Aperçu / Preview

> *Note : Les captures d'écran ci-dessous reflètent la nouvelle interface "Matte" avec la sauvegarde automatique.*

### Liste des dossiers (Statistiques)

![Liste des dossiers](docs/screenshots/dossiers-list.png)

### Hub d'investigation (Carnets)

![Hub d'investigation](docs/screenshots/dossier-hub.png)

### Graphe & Transformations

![Analyse Graphe](docs/screenshots/sherlock-transform.png)

## Fonctionnalités / Features

| Module | Description |
|--------|-------------|
| **Dossiers** | Investigations isolées avec métadonnées et accès rapide aux carnets |
| **Carnets** | Notes, chronologie, listes — typés selon le besoin d'investigation |
| **Graphe** | Canvas Cytoscape, transforms OSINT, navigation relationnelle |
| **Provenance** | Source, observation, evidence, confiance (CONFIRMED → CONTRADICTED) |
| **Notes** | Saisie datée, édition et suppression dans les carnets |
| **Import / Export** | Transfert de données (JSON/CSV) depuis/vers le graphe |
| **Recherche décès INSEE** | Fichier public des décès en France (depuis 1970) — graphe, fiche personne, mode local optionnel |
| **Auto-save** | Sauvegarde transparente et continue de l'investigation |
| **Corbeille** | Dossiers supprimés — restauration ou suppression définitive |

## Stack

- **Frontend**: Electron + React 18 + TypeScript + Vite + Cytoscape.js
- **Backend**: FastAPI + Python 3.11 + asyncio + SQLite
- **Realtime**: Socket.IO (via `main:asgi_app`)
- **Domain API**: `/api/v1/` (dossiers, carnets, entités, provenance)

*Planifié : Neo4j, Agent-OS orchestrator*

## Déploiement (Streamlit Cloud)

Hébergement cloud via Streamlit Community Cloud — backend Python intégré.

```bash
# Cloud : pousser sur GitHub, configurer sur share.streamlit.io
# Main file : streamlit_app.py
```

Guide complet : [`deploy/streamlit-cloud.md`](deploy/streamlit-cloud.md)

> **UI locale complète** (Matte & Vintage, Cytoscape) : `npm run dev` → http://localhost:5173  
> Streamlit Cloud sert l'accès cloud ; le frontend React reste dans `frontend/` pour le dev et Electron.

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

### Données de démo / Demo data

Pour peupler un dossier de test (carnets, entités, graphe) :

```bash
cd backend && .venv/bin/python scripts/seed_test_dossier.py
```

### Electron desktop

```bash
cd frontend && npm run electron:dev
```

## Architecture

```
OSINTGraph/
  frontend/           React + Electron UI (Matte & Vintage) — dev local
  streamlit_app.py    Entry point Streamlit Cloud
  ui/                 Vues Streamlit (déploiement cloud)
  backend/            FastAPI + plugins OSINT + SQLite
  deploy/             Guides déploiement (streamlit-cloud.md)
  requirements.txt    Dépendances Streamlit Cloud (racine)
```

**Contexte projet** — [`AGENTS.md`](AGENTS.md) (guide agents, routing, conventions) · [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md) (UX investigation, carnets, navigation)

## Entity Types (Registry dynamique)

L'architecture est passée d'Enums rigides à un `EntityTypeRegistry` dynamique permettant l'ajout via plugins.
Entités par défaut : `PERSON` · `EMAIL` · `DOMAIN` · `IP` · `USERNAME` · `ORGANIZATION` · `PHONE` · `LOCATION` · `SOCIAL_ACCOUNT`

Domain model (v2) extensible.

## Built-in Transforms

| Transform | Input | Output | Fournisseur |
|-----------|-------|--------|-------------|
| DNS Lookup | Domain | IP | - |
| Whois Lookup | Domain | Organization | - |
| HIBP Lookup | Email | Domain (breach) | - |
| Shodan Lookup | IP, Domain | Organization, Location, Port | shodan |
| Sherlock Lookup | Username | Social Account | - |
| IP Geolocation | IP | Location, Organization | - |
| Phone Lookup | Phone | Location, Organization | - |
| Holehe Lookup | Email | Username | - |
| Maigret Lookup | Username | Social Account | - |
| SpiderFoot Scan | Domain, IP, Email, Username, Phone, Person | Multi-types | spiderfoot |
| **Death Search (INSEE)** | Person | Person, Location | data.gouv.fr / DuckDB |

Guide détaillé recherche décès : [`docs/DEATH_SEARCH.md`](docs/DEATH_SEARCH.md)

### Configuration recherche décès (optionnel)

```bash
# Backend — fichier Parquet local ou dossier parts/ partitionné
DEATH_RECORDS_PATH=/chemin/vers/parts

# Frontend — recherche 100 % locale (DuckDB-WASM, voir arbre-local)
VITE_DEATH_RECORDS_BASE_URL=https://pub-xxxxx.r2.dev/parts
```

Voir [`docs/DEATH_SEARCH.md`](docs/DEATH_SEARCH.md) pour le pipeline de préparation des données.

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
