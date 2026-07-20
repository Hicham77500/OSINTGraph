# Déploiement OSINTGraph — Streamlit Cloud

Guide pour héberger OSINTGraph sur [Streamlit Community Cloud](https://share.streamlit.io).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Développement local (UI complète Matte & Vintage)      │
│  npm run dev  →  React + Vite (5173) + FastAPI (8000)   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Production cloud (Streamlit Cloud)                     │
│  streamlit_app.py  →  ui/ + backend Python (SQLite)     │
└─────────────────────────────────────────────────────────┘
```

L'interface **React / Cytoscape** (refonte Matte) reste dans `frontend/` pour le développement local et desktop Electron.  
Streamlit Cloud exécute `streamlit_app.py` avec le backend Python intégré (imports directs, pas de serveur HTTP séparé).

> Pour l'UI React complète en production, hébergez le build Vite (`npm run build`) sur Netlify/Vercel et l'API FastAPI sur Render/Railway. Streamlit Cloud ne sert pas de SPA React nativement.

## Prérequis

- Compte GitHub avec le dépôt OSINTGraph
- Compte [Streamlit Cloud](https://share.streamlit.io) (gratuit)

## Déploiement

### 1. Pousser sur GitHub

```bash
git push origin main
```

### 2. Créer l'app sur Streamlit Cloud

1. [share.streamlit.io](https://share.streamlit.io) → **Create app**
2. Repository : `Hicham77500/OSINTGraph`
3. Branch : `main`
4. **Main file path** : `streamlit_app.py`
5. **Requirements file** : `requirements.txt` (racine du dépôt)

### 3. Secrets (optionnel)

Dans **App settings → Secrets**, ajouter :

```toml
SHODAN_API_KEY = "votre-clé"
HIBP_API_KEY = "votre-clé"
SQLITE_PATH = "data/osintgraph.db"
```

Voir `.streamlit/secrets.toml.example` pour le modèle local.

### 4. Redéployer

Streamlit Cloud rebuild automatiquement à chaque push sur `main`.

## Développement local

### UI complète (React — recommandé)

```bash
npm install
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd .. && npm run dev
```

→ http://localhost:5173 (interface Matte & Vintage)

### Preview déploiement cloud (Streamlit)

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

→ http://localhost:8501

## Données

| Environnement | Persistance |
|---------------|-------------|
| Local | `data/osintgraph.db` (gitignored) |
| Streamlit Cloud | **Éphémère** — reset au redémarrage |

Pour des données persistantes en cloud, configurez un stockage externe (S3, Supabase, etc.) — non implémenté par défaut.

### Seed de démo

```bash
cd backend && python scripts/seed_test_dossier.py
```

## Sécurité

- Ne commitez jamais de secrets (`.env`, `secrets.toml`)
- Streamlit Cloud : secrets via l'interface admin uniquement
- OSINTGraph ne journalise pas d'emails, téléphones ou clés API
- Sources ouvertes et données analyste uniquement

## Dépannage

| Problème | Action |
|----------|--------|
| `ModuleNotFoundError: ui` | Vérifier que `streamlit_app.py` est à la racine et `ui/` présent |
| Base vide après reboot | Normal sur Streamlit Cloud (SQLite éphémère) |
| Transform Shodan échoue | Ajouter `SHODAN_API_KEY` dans les secrets |
| UI différente du local | Normal : cloud = Streamlit, local = React |

## Commandes utiles

```bash
npm run dev              # React + API (UI complète)
npm run dev:streamlit    # Preview Streamlit local
cd backend && pytest     # Tests backend
```
