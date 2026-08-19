# Recherche décès INSEE — OSINTGraph

> Interroger le fichier public des personnes décédées en France (INSEE / data.gouv.fr, ~29 M d'enregistrements depuis 1970).  
> Inspiré de l'architecture [arbre-local](https://github.com/sosoj92/arbre-local).

## Ce que fait la fonctionnalité

| Capacité | Description |
|----------|-------------|
| **Plugin `death_search`** | Transform sur nœud `PERSON` dans le graphe (panneau Transforms) |
| **Modal « Recherche de décès »** | Depuis la fiche personne (`PersonViewPage`) |
| **Mode navigateur (optionnel)** | DuckDB-WASM + Parquet distant — aucun nom envoyé au serveur |
| **Demande d'acte** | Mailto prérempli avec garde-fous légaux (filiation) |

Les résultats sont des **pistes UNVERIFIED** — homonymes fréquents. Seul un acte d'état civil fait foi.

## Ce que ce n'est pas

- Pas un arbre généalogique ni une filiation automatique
- Pas de téléchargement d'actes officiels
- Pas de couverture avant 1970 (index INSEE)
- Pas d'envoi automatique de courriels (ouverture du client mail de l'analyste uniquement)

## Utilisation dans l'UI

### Graphe

1. Sélectionner un nœud **PERSON**
2. Panneau Inspector → onglet **Transforms**
3. Lancer **Recherche décès INSEE**

### Fiche personne

1. Route `/dossier/:id/person/:entityId`
2. Onglet **Vue d'ensemble** → **Rechercher un décès**
3. Filtres : prénom, commune, département, plage d'années de naissance

### Demande d'acte (mailto)

| Type d'acte | Règle | Comportement UI |
|-------------|-------|-----------------|
| **Acte de décès** | Communicable depuis 2008 sans filiation | Bouton direct |
| **Acte de naissance** (< 75 ans) | Mairie — identité + lien de filiation requis | Case à cocher obligatoire avant mailto |
| **Acte de naissance** (≥ 75 ans) | Archives départementales | Bouton direct + lien [FranceArchives](https://francearchives.gouv.fr/fr/annuaire) |

OSINTGraph **ne vérifie pas** l'identité ni le lien de filiation — responsabilité de l'analyste.

## Configuration des données

Le fichier INSEE n'est **pas** inclus dans le dépôt. Télécharger sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/fichier-des-personnes-decedees/) : **« Agrégation des fichiers des personnes décédées »** (format **Parquet**).

### Option A — Backend (DuckDB Python)

Variables dans `backend/.env` :

```bash
# Fichier unique .parquet OU dossier parts/ partitionné (voir arbre-local)
DEATH_RECORDS_PATH=/chemin/vers/parts

# OU URL CDN avec requêtes HTTP Range (CORS + ExposeHeaders)
DEATH_RECORDS_BASE_URL=https://pub-xxxxx.r2.dev/parts
```

Le plugin charge uniquement la partition correspondant à la première lettre du nom (`lettre=D/data.parquet`).

### Option B — Navigateur (DuckDB-WASM, recommandé pour la confidentialité)

Variable à la racine ou dans `frontend/.env` :

```bash
VITE_DEATH_RECORDS_BASE_URL=https://pub-xxxxx.r2.dev/parts
```

La recherche s'exécute dans le navigateur ; seules des requêtes `Range: bytes=…` partent vers le CDN.

### Préparation des partitions (pipeline arbre-local)

Résumé — voir le [README arbre-local](https://github.com/sosoj92/arbre-local) pour le détail :

1. Télécharger le Parquet agrégé data.gouv.fr
2. Filtrer `opposition = false` (obligation légale)
3. Trier par `nom, prenoms` puis partitionner par première lettre (`parts/lettre=X/data.parquet`)
4. Héberger sur stockage objet avec **CORS** et **HTTP Range** (Cloudflare R2, S3, etc.)

## Fichiers implémentés

| Fichier | Rôle |
|---------|------|
| `backend/plugins/death_search/` | Plugin transform (manifest + DuckDB) |
| `frontend/src/services/deathSearch.ts` | API backend + client WASM |
| `frontend/src/components/modals/DeathSearchModal.tsx` | UI recherche |
| `frontend/src/components/modals/ActRequestButtons.tsx` | Demande d'acte encadrée |
| `frontend/src/utils/civilRegistryRequest.ts` | Éligibilité légale + mailto |
| `backend/tests/test_death_search.py` | Tests plugin |

## Provenance et éthique

- Source : INSEE / data.gouv.fr — Licence Ouverte 2.0
- `collection_method`: `OFFICIAL_API`
- Statut par défaut : `UNVERIFIED`
- Exclure les lignes `opposition = true` à la source ou en requête
- Ne jamais logger noms/dates dans les logs backend

## Licence des données

- **Fichier des personnes décédées** — INSEE / data.gouv.fr, Licence Ouverte 2.0
- Mentionner la source et exclure les oppositions à la rediffusion

## Dépannage

| Problème | Piste |
|----------|--------|
| « Données non configurées » | Définir `DEATH_RECORDS_PATH` ou `VITE_DEATH_RECORDS_BASE_URL` |
| 0 résultat | Affiner prénom, commune, département ; noms en MAJUSCULES dans l'index |
| Mode client ne démarre pas | Vérifier CORS et `ExposeHeaders: Content-Range` sur le bucket |
| DuckDB erreur `opposition` | Données déjà filtrées — le plugin retente sans ce filtre |

## Références

- [arbre-local](https://github.com/sosoj92/arbre-local) — architecture Parquet + DuckDB-WASM
- [data.gouv.fr — décès](https://www.data.gouv.fr/fr/datasets/fichier-des-personnes-decedees/)
- [FranceArchives — annuaire](https://francearchives.gouv.fr/fr/annuaire)
