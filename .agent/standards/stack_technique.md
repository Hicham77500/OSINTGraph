# Stack Technique OsintGraph

## Code Frontend
- **Langage / Framework** : TypeScript, React 18
- **Bundler** : Vite (Rapide, HMR via `npm run dev`)
- **State** : Zustand (`graphStore.ts` pour NodeData/EdgeData).
- **Graphing** : Cytoscape.js (`cytoscape-cola` & `cytoscape-dagre`). Éviter SVG inline si problématique, utiliser le Canvas HTML pour l'iconographie.
- **Styling** : CSS natif (`.css`) avec Variables CSS (`:root`). Design imposé : UI translucide (*Dark Glassmorphism*).

## Wrapper Desktop
- **Framework** : Electron
- **Sécurité** : `nodeIntegration: false`, `contextIsolation: true`.
- **Preload** : Obligatoire pour exposer `window.osint.api`.

## Code Backend
- **Langage** : Python 3.11+
- **Serveur web** : FastAPI avec serveur Uvicorn (port par défaut 8000).
- **Communication** : Socket.IO via `python-socketio` (namespace async) activé avec l'applicationASGI de FastAPI.
- **Base de données** : SQLite local avec `aiosqlite` pour le logging et les workspaces.
- **Orchestration Agent OS** : Gérée via le module `agent_os.py` pour chainer les transforms (Shodan, WHOIS, DNS).

## Conventions de Code
- **TypeScript** : Noms de variables en `camelCase`, Interfaces en `PascalCase`. Typage strict (pas de `any`).
- **Python** : Code formaté selon `PEP8`, variables en `snake_case`, classes en `PascalCase`. Type hints obligatoires (`def foo(bar: str) -> dict:`).
- **Commentaires** : Explications des blocs complexes uniquement. Les signatures et variables doivent être auto-descriptives.
