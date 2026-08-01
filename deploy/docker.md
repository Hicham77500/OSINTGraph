# Déploiement OSINTGraph — Docker

Guide pour déployer l'interface **React Matte & Vintage** + **API FastAPI** sur une machine ou un VPS, avec **SpiderFoot** en option.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Navigateur → http://<hôte>:8080 (nginx)                    │
│    ├── /              → SPA React (build Vite)              │
│    ├── /transforms    → proxy → api:8000                    │
│    ├── /graph         → proxy → api:8000                    │
│    └── /socket.io     → WebSocket → api:8000                │
└─────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
   frontend:80                    api:8000
   (nginx)                        SQLite → volume osintgraph-data

   [optionnel, profil spiderfoot]
         spiderfoot:5001  ←  plugin spiderfoot_scan (modules passifs)
```

Le frontend React reste dans `frontend/` — **ne pas le supprimer**. Streamlit Cloud reste une option séparée (`deploy/streamlit-cloud.md`).

## Prérequis

- Docker 24+ et Docker Compose v2
- 2 Go RAM minimum (4 Go recommandé avec SpiderFoot)
- Ports libres : `8080` (UI), `8000` (API directe), `5001` (SpiderFoot optionnel)

## Démarrage rapide

```bash
git clone https://github.com/Hicham77500/OSINTGraph.git
cd OSINTGraph
cp .env.example .env
docker compose up --build
```

- **Interface** : http://localhost:8080
- **API / health** : http://localhost:8000/health
- **Logs** : `docker compose logs -f api frontend`

Arrêt : `docker compose down`  
Suppression des volumes (données SQLite) : `docker compose down -v`

## Avec SpiderFoot (optionnel)

SpiderFoot est **désactivé par défaut**. Le plugin `spiderfoot_scan` utilise une liste de **modules passifs** (DNS, WHOIS, certificats, recherche publique) — pas de scan actif ni d'intrusion.

```bash
docker compose --profile spiderfoot up --build
```

- UI SpiderFoot : http://localhost:5001
- Variable `SPIDERFOOT_URL=http://spiderfoot:5001` (déjà dans `.env.example`)

> **Éthique OSINT** : n'activez que des modules adaptés à vos sources ouvertes et à votre cadre légal. OSINTGraph ne présente jamais les sorties IA ou automatisées comme des faits confirmés.

## Configuration

Éditez `.env` à la racine :

| Variable | Description |
|----------|-------------|
| `FRONTEND_PORT` | Port hôte pour l'UI (défaut `8080`) |
| `API_PORT` | Port hôte pour l'API directe (défaut `8000`) |
| `VITE_API_BASE` | Laisser **vide** en Docker (proxy nginx same-origin) |
| `CORS_ORIGINS` | Origines autorisées pour CORS et Socket.IO |
| `SHODAN_API_KEY` | Clé Shodan pour `shodan_lookup` |
| `HIBP_API_KEY` | Clé HIBP pour `hibp_lookup` |
| `OSINTGRAPH_AUTH_DISABLED` | `true` en local ; `false` en production si auth activée |
| `OSINTGRAPH_SESSION_SECRET` | Secret de session — **à changer en production** |

Les transforms **Maigret**, **Holehe** et **Sherlock** sont installés dans l'image API via `backend/requirements.txt`.

## WebSocket (transforms en temps réel)

L'UI s'abonne aux événements Socket.IO pendant l'exécution d'un transform :

- `transform:start` — démarrage
- `transform:log` / `transform:progress` — lignes de log et progression
- `transform:result` — résultat final (nœuds + arêtes)
- `transform:error` — erreur

En Docker, nginx proxifie `/socket.io` vers l'API. Aucune configuration supplémentaire si `VITE_API_BASE` est vide.

## Production (VPS)

1. Copier le dépôt sur le serveur
2. Configurer `.env` (`CORS_ORIGINS=https://votre-domaine.fr`, secret de session fort)
3. Placer un reverse proxy TLS (Caddy, Traefik, nginx) devant le port `8080`
4. Sauvegarder le volume `osintgraph-data` régulièrement

Exemple Caddy :

```caddy
votre-domaine.fr {
    reverse_proxy localhost:8080
}
```

## Dépannage

| Problème | Piste |
|----------|--------|
| UI blanche | `docker compose logs frontend` — vérifier le build Vite |
| Transforms sans log live | Vérifier la connexion WS dans les DevTools (onglet Network → WS) |
| SpiderFoot injoignable | Lancer avec `--profile spiderfoot` ; tester `curl http://localhost:5001/scanlist` |
| Maigret / Holehe absents | Reconstruire l'image API : `docker compose build --no-cache api` |

## Fichiers créés

| Fichier | Rôle |
|---------|------|
| `backend/Dockerfile` | Image FastAPI + plugins OSINT |
| `frontend/Dockerfile` | Build Vite + nginx |
| `frontend/nginx.conf` | Proxy API + WebSocket |
| `docker-compose.yml` | Orchestration services |
| `.env.example` | Variables d'environnement |
| `deploy/spiderfoot/Dockerfile` | Image SpiderFoot v4.0 (profil optionnel) |
