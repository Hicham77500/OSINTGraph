# OSINTGraph — Guide de démarrage

> Choisissez le mode qui correspond à votre usage. L'interface **React** est la référence complète ; **Streamlit** sert l'accès cloud simplifié ; **Docker** déploie React + API en production.

## Choisir son interface

| Mode | Commande | Idéal pour |
|------|----------|------------|
| **React (local)** | `npm run dev` | Analyste au quotidien — graphe Cytoscape, transforms temps réel, Electron |
| **Streamlit (preview)** | `npm run dev:streamlit` | Tester l'UI cloud en local (:8501) |
| **Docker (production)** | `docker compose up --build` | VPS / équipe — React sur :8080 + API :8000 |
| **Streamlit Cloud** | GitHub → share.streamlit.io | Démo rapide sans serveur (SQLite éphémère) |

> Streamlit ne remplace pas React : pas de recherche décès INSEE avancée, pas de DuckDB-WASM, graphe PyVis au lieu de Cytoscape. Voir [`deploy/streamlit-cloud.md`](../deploy/streamlit-cloud.md).

## Installation rapide (Windows)

```powershell
git clone https://github.com/Hicham77500/OSINTGraph.git
cd OSINTGraph
.\scripts\setup.ps1
npm run dev
```

- Frontend : http://localhost:5173  
- API : http://127.0.0.1:8000/health  

## Installation rapide (macOS / Linux)

```bash
git clone https://github.com/Hicham77500/OSINTGraph.git
cd OSINTGraph
./scripts/setup.sh
npm run dev
```

## Données de démo

Pour explorer sans partir de zéro :

```bash
cd backend
.venv\Scripts\python scripts\seed_test_dossier.py   # Windows
# .venv/bin/python scripts/seed_test_dossier.py     # macOS/Linux
```

Dans l'UI Streamlit, le bouton **« Charger la démo »** sur la page d'accueil exécute le même script.

## Configuration (clés API)

Copiez les fichiers d'exemple :

| Fichier | Usage |
|---------|--------|
| `backend/.env` | Dev local (Shodan, etc.) |
| `.env` | Docker Compose |
| `.streamlit/secrets.toml` | Preview Streamlit local |

Clés courantes :

```env
SHODAN_API_KEY=
SPIDERFOOT_URL=http://localhost:5001   # si profil Docker spiderfoot
DEATH_RECORDS_PATH=                    # optionnel — recherche décès INSEE
```

Pas d'écran Paramètres dans l'UI : les clés passent par variables d'environnement ou secrets Streamlit.

## Premier parcours analyste (React)

1. **Créer un dossier** — page d'accueil `/`
2. **Ouvrir le graphe complet** — carte principale du hub dossier
3. **Ajouter une entité** — panneau gauche (personne, email, domaine…)
4. **Lancer un transform** — clic droit ou panneau Transforms (Sherlock, DNS, etc.)
5. **Explorer les carnets** — Personnes, Notes, Chronologie sous le hub

Le bandeau d'accueil s'affiche automatiquement sur un dossier vide.

## Fork et personnalisation

Pour adapter OSINTGraph à votre organisation :

1. Fork sur GitHub : bouton **Fork** sur [Hicham77500/OSINTGraph](https://github.com/Hicham77500/OSINTGraph)
2. Clonez **votre** fork : `git clone git@github.com:VOTRE_COMPTE/OSINTGraph.git`
3. Branchez une branche : `git checkout -b feature/ma-customisation`
4. Consultez [`CONTRIBUTING.md`](../CONTRIBUTING.md) pour les conventions

## Documentation complémentaire

| Document | Contenu |
|----------|---------|
| [`README.md`](../README.md) | Vue d'ensemble, plugins, tests |
| [`AGENTS.md`](../AGENTS.md) | Guide agents IA |
| [`docs/PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) | UX investigation, routing |
| [`docs/DEATH_SEARCH.md`](DEATH_SEARCH.md) | Recherche décès INSEE |
| [`deploy/docker.md`](../deploy/docker.md) | Déploiement Docker |
| [`deploy/streamlit-cloud.md`](../deploy/streamlit-cloud.md) | Streamlit Cloud |
