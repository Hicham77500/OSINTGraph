# Architecture OsintGraph

## Vue d'ensemble (Global Architecture)
OsintGraph est une application Desktop modulaire hybride composée de :
1. **Frontend (React + Vite)** : Single Page Application gérant l'UI/UX et le rendu du graphe.
2. **Wrapper Desktop (Electron)** : Conteneur natif avec `contextBridge` strict pour la communication inter-processus.
3. **Backend Orchestrateur (FastAPI + Agent-OS)** : Serveur local asynchrone orchestrant l'exécution des *Transforms* (plugins d'enrichissement OSINT) et la gestion des données.

## 1. Frontend
- **Gestion d'état (State Management)** : **Zustand** est le standard exclusif pour l'état global (`useGraphStore` pour le graphe, `useUIStore` pour l'interface). Interdiction des Contexts lourds ou de Redux. Prop-drilling strictement prohibé au-delà de 2 niveaux.
- **Moteur de Graphe** : **Cytoscape.js**. 
  - *Règle de style* : Les styles de nœuds doivent refléter le dictionnaire `NODE_TYPE_CONFIG` (couleurs, type). 
  - *Performances* : Utilisation des headless layouts (`cola`, `dagre`) et de la mutabilité contrôlée (batch updates) dans Cytoscape, tout en gardant Zustand synchronisé.
- **UI/UX** : Composants fonctionnels (`FC`). L'interface doit obéir au paradigme *Dark Glassmorphism* (fonds `rgba` translucides, bordures subtiles violet/bleu `var(--accent-primary)`).

## 2. Backend & Agent-OS
- **Architecture Modulaire** :
  - `routers/` : Endpoints REST et WebSocket (FastAPI).
  - `transforms/` : Scripts de collecte OSINT granulaires. Un fichier = un service/plugin (ex: `shodan_lookup.py`).
  - `agents/` : Orchestrateurs complexes (pipelines Agent-OS).
  - `db/` : Persistance.
- **Temps Réel (WebSockets)** : Communication bidirectionnelle via **Socket.IO**. L'orchestrateur informe le frontend de chaque nœud trouvé en temps réel (`transform_progress`, `transform_result_node`).
- **Persistance** : SQLite via `aiosqlite` pour le stockage local (workspaces, entités, relations).

## 3. Communication (IPC & Réseau)
- **Localhost API** : Le frontend (port 5173 / Electron BrowserView) communique avec le backend (port 8000) via REST pour la configuration et Socket.IO pour les pipelines.
- **Sécurité ContextBar** : Electron n'a PAS de `nodeIntegration`. L'accès natif se fait via `window.osint.api`.
