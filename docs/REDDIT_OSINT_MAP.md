# Cartographie Reddit → OSINTGraph

Synthèse des outils **open source** fréquemment cités sur Reddit (r/OSINT, r/osinttools) et de leur statut dans OSINTGraph.  
**Ce document ne encourage pas** l’usage de dumps, dark web automatisé ou bases volées.

## Déjà couverts par OSINTGraph

| Reddit / communauté | GitHub / service | OSINTGraph |
|---------------------|------------------|------------|
| Maigret | [soxoj/maigret](https://github.com/soxoj/maigret) | `maigret_lookup` |
| Sherlock | [sherlock-project/sherlock](https://github.com/sherlock-project/sherlock) | `sherlock_lookup` |
| Holehe | holehe | `holehe_lookup` |
| PhoneInfoga | [sundowndev/phoneinfoga](https://github.com/sundowndev/phoneinfoga) | Partiel : `phone_lookup` + recherche web ; plugin PhoneInfoga **planifié** |
| HIBP | haveibeenpwned.com API | `hibp_lookup` |
| SpiderFoot | spiderfoot | `spiderfoot_scan` |
| Multi-moteurs / nom | threads « OSINT tools » | `web_search_assistants`, modale **Recherche web & social** |
| Reverse image | divers | `image_investigation`, modale **Recherche visuelle** |

Fil de référence : [r/OSINT — OSINT tools](https://www.reddit.com/r/OSINT/comments/ud5j1i/osint_tools/).

## Services commerciaux / API (pas de scrape)

| Nom | Lien | Intégration |
|-----|------|-------------|
| IntelBase | [intelbase.is](https://intelbase.is) | Planifié — API payante ; wrapper [IntelBase-CLI](https://github.com/cons0le7/IntelBase-CLI) |
| IntelX | [intelx.io](https://intelx.io) | Planifié — [IntelligenceX/SDK](https://github.com/IntelligenceX/SDK) + clé analyste |

## Exclus (voir [OSINT_TOOLS_SCOPE.md](./OSINT_TOOLS_SCOPE.md))

| Reddit / GitHub | Motif |
|-----------------|--------|
| Telespot + DeHashed | [thumpersecure/Telespot](https://github.com/thumpersecure/Telespot) — fuites / credentials |
| VoidAccess | [KatrielMoses/voidaccess](https://github.com/KatrielMoses/voidaccess) — dark web OSINT automatisé |
| Godseye | dark web + extraction creds |
| OSINT-D2 | [Doble-2/osint-d2](https://github.com/Doble-2/osint-d2) — évaluer au cas par cas ; HIBP API seulement si connecteur dédié |

## Ajouter un outil Reddit de façon propre

1. Vérifier [OSINT_TOOLS_SCOPE.md](./OSINT_TOOLS_SCOPE.md) (légal + éthique).
2. Plugin sous `backend/plugins/<id>/` + provenance dans `observations`.
3. Entrée dans `backend/config/transform_hub_catalog.json`.
4. Tests `backend/tests/test_plugins.py` + doc [TRANSFORM_HUB.md](./TRANSFORM_HUB.md).
