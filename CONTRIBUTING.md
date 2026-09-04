# Contribuer à OSINTGraph

Merci de votre intérêt pour OSINTGraph. Ce dépôt est conçu pour être **fork-friendly** : vous pouvez l'adapter à votre workflow d'investigation tout en respectant les limites éthiques du projet.

## Fork workflow (recommandé)

```bash
# 1. Fork via l'interface GitHub, puis :
git clone https://github.com/VOTRE_COMPTE/OSINTGraph.git
cd OSINTGraph
git remote add upstream https://github.com/Hicham77500/OSINTGraph.git

# 2. Branche de travail
git checkout -b feature/ma-fonctionnalite

# 3. Synchroniser avec l'amont
git fetch upstream
git merge upstream/main

# 4. Pousser sur votre fork
git push -u origin feature/ma-fonctionnalite
```

Ouvrez une Pull Request vers `Hicham77500/OSINTGraph:main` depuis votre fork.

## Setup développeur

```bash
npm install
./scripts/setup.sh          # ou .\scripts\setup.ps1 sur Windows
npm run dev                 # React + API
npm run dev:streamlit       # preview cloud
```

Tests :

```bash
cd backend && .venv/bin/pytest    # ou .venv\Scripts\pytest
cd frontend && npm test
```

## Conventions

- **Minimal diffs** — pas de refonte massive sans spec dans `.agent/specs/`
- **Provenance obligatoire** — toute donnée OSINT : source, `collectedAt`, confiance
- **Plugins** — nouveaux transforms dans `backend/plugins/` (`plugin.json` + `plugin.py`)
- **i18n React** — textes UI dans `frontend/src/i18n/locales/en.ts` et `fr.ts`
- **Éthique** — lire `.cursor/rules/investigation-ethics.mdc` avant tout connecteur

## Zones du dépôt

| Zone | Rôle | Modifier si… |
|------|------|----------------|
| `frontend/` | UI React référence | UX graphe, modals, routing |
| `ui/` | UI Streamlit cloud | Accès cloud simplifié |
| `backend/plugins/` | Transforms OSINT | Nouveau plugin |
| `backend/transforms/` | Legacy | Éviter — migrer vers plugins |
| `docs/` | Documentation utilisateur | Parcours, guides |
| `deploy/` | Docker, Streamlit Cloud | Infra |

## Pull requests

1. Décrivez le **pourquoi** (cas analyste, pas seulement le diff)
2. Mentionnez les tests exécutés
3. Pas de secrets (.env, tokens) dans le commit
4. Les hypothèses IA restent des **hypothèses** — jamais présentées comme faits

## Signaler un problème

Ouvrez une [issue GitHub](https://github.com/Hicham77500/OSINTGraph/issues) avec :

- Mode utilisé (React / Streamlit / Docker)
- Étapes de reproduction
- Comportement attendu vs observé

## Licence et données sensibles

OSINTGraph traite des données personnelles potentiellement sensibles. N'utilisez que des sources ouvertes ou des données fournies volontairement par l'analyste. Ne commitez jamais de données d'investigation réelles.
