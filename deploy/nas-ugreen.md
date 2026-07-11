# Déploiement OSINTGraph sur NAS UGREEN (DXP2800)

Guide pour un déploiement **self-hosted** avec Docker, SQLite sur volume persistant et accès via Tailscale.

## Prérequis

- NAS UGREEN DXP2800 avec **Docker** activé
- **Tailscale** installé sur le NAS (recommandé pour l'accès distant)
- Accès SSH ou interface Docker du NAS
- ~2 Go d'espace disque pour images + données

## Architecture

```
Navigateur / Tailscale Serve
        │
        ▼
   web (nginx:80) ──► port hôte 8080
        │ proxy /api, /graph, /transforms, /workspaces, /health, /socket.io
        ▼
   api (uvicorn:8000) — réseau interne Docker uniquement
        │
        ▼
   volume osintgraph_data → /data/osintgraph.db
```

Un seul fichier SQLite contient les tables domaine (relationnel) et le blob graphe legacy.

## Installation

### 1. Copier le projet sur le NAS

```bash
# Sur le NAS (SSH) ou depuis votre machine puis rsync/scp
git clone https://github.com/votre-org/OSINTGraph.git
cd OSINTGraph
```

Vous pouvez aussi copier uniquement les fichiers nécessaires : `backend/`, `frontend/`, `docker-compose.yml`, `.env.docker.example`.

### 2. Configurer l'environnement

```bash
cp .env.docker.example .env
nano .env   # ou éditeur de l'interface Docker
```

Variables importantes :

| Variable | Description |
|----------|-------------|
| `OSINTGRAPH_PORT` | Port exposé sur le NAS (défaut `8080`) |
| `OSINTGRAPH_AUTH_DISABLED` | `false` en production |
| `OSINTGRAPH_SESSION_SECRET` | Secret long et aléatoire (`openssl rand -hex 32`) |
| `CORS_ORIGINS` | URL(s) d'accès (IP locale, hostname Tailscale) |
| `SHODAN_API_KEY` / `HIBP_API_KEY` | Optionnel — transforms concernés |

### 3. Lancer la stack

```bash
docker compose up -d --build
```

Vérifier l'état :

```bash
docker compose ps
docker compose logs -f api
curl http://localhost:8080/health
```

### 4. Accès

- **Réseau local** : `http://<ip-nas>:8080`
- **Tailscale Serve** (recommandé) : exposer le port `8080` du NAS sur votre tailnet HTTPS
- Ne pas exposer le port API (`8000`) — il reste sur le réseau Docker interne

### 5. Authentification

Avec `OSINTGRAPH_AUTH_DISABLED=false`, chaque requête API doit inclure :

```
X-OSINTGraph-Session: <valeur de OSINTGRAPH_SESSION_SECRET>
```

Configurez un reverse proxy ou un client qui envoie cet en-tête si vous accédez via Tailscale Serve.

> **Note** : l'UI web actuelle cible le mode dev (auth désactivée). Pour un déploiement NAS avec auth activée, configurez le secret côté client ou gardez l'accès limité au tailnet via Tailscale sans exposition publique.

## Sauvegarde

Le volume nommé `osintgraph_data` contient `/data/osintgraph.db`.

```bash
# Arrêt propre recommandé
docker compose stop api

# Copie depuis le conteneur
docker compose run --rm -v osintgraph_data:/data alpine cp /data/osintgraph.db /data/backup-$(date +%Y%m%d).db

# Redémarrage
docker compose start api
```

Sauvegardez aussi le fichier `.env` (hors dépôt git) — il contient les secrets.

## Données de démo (optionnel)

```bash
docker compose exec api python scripts/seed_test_dossier.py
```

## Mise à jour

```bash
git pull
docker compose up -d --build
```

Les données persistent dans le volume `osintgraph_data`.

## Sécurité

- **Tailscale only** : évitez d'exposer le port 8080 sur Internet sans protection
- **Auth activée** : `OSINTGRAPH_AUTH_DISABLED=false` + secret fort
- **Secrets** : ne commitez jamais `.env`
- **Logs** : le backend ne journalise pas d'emails, téléphones ou clés API
- **Sauvegardes** : planifiez une copie régulière de `osintgraph.db`

## Dépannage

| Problème | Action |
|----------|--------|
| `api` unhealthy | `docker compose logs api` — vérifier permissions volume `/data` |
| WebSocket déconnecté | vérifier proxy nginx `/socket.io/` et `CORS_ORIGINS` |
| Base vide au redémarrage | confirmer que le volume `osintgraph_data` est bien attaché |
| Erreur 401 | auth activée — envoyer `X-OSINTGraph-Session` ou désactiver temporairement pour test local |

## Commandes utiles

```bash
docker compose up -d --build    # build + démarrage
docker compose down             # arrêt (volume conservé)
docker compose down -v          # arrêt + suppression volume (⚠ perte données)
docker compose logs -f web api  # logs combinés
```
