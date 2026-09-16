# Périmètre des outils OSINT (intégrés vs exclus)

OSINTGraph n’est pas un agrégateur de fuites ni un scanner dark web. Ce document fixe ce qui est **intégré**, **planifié** et **hors périmètre** (y compris les outils souvent cités sur Reddit).

## Intégré aujourd’hui

| Capacité | Plugins / UI | Notes |
|----------|----------------|-------|
| Pseudo → profils | `sherlock_lookup`, `maigret_lookup` | Exécution locale des binaires/outils configurés |
| E-mail → comptes | `holehe_lookup` | Signaux publics d’inscription |
| E-mail → violations **référencées** | `hibp_lookup` | API officielle `HIBP_API_KEY` — pas de mode demo |
| Téléphone → métadonnées | `phone_lookup` | lib `phonenumbers` (pays, opérateur) |
| Web / nom | `web_search_assistants` | **Hits réels** (Brave, DDG, Wikipedia) — pas de nœuds « Google » |
| Réseaux sociaux | `social_web_search` | Pages publiques via recherche `site:` (Brave recommandé) |
| Forums / Reddit (index public) | `forum_search_assistants` | Mots-clés **choisis par l’analyste** |
| Immatriculation | `vehicle_plate_search` + nœud `plate` | Mentions web publiques uniquement |
| Image | `image_investigation` + modale **Recherche visuelle** | Upload local, liens Lens/Bing/Yandex/TinEye |
| Lieu | `nominatim_geocode` | API OpenStreetMap Nominatim |
| CTI / réseau | Shodan, VT, OTX, urlscan, crt.sh, DNS, WHOIS, etc. | Voir [TRANSFORM_HUB.md](./TRANSFORM_HUB.md) |
| Hub partenaires | UI **Transform hub** + `GET /transforms/hub` | Catalogue Maltego-style |
| Clés API | `GET /transforms/api-keys` + icône **ℹ** | Liens d’inscription (`.env`) |

### Variables d’environnement utiles

```env
BRAVE_SEARCH_API_KEY=      # Résultats nominatifs web / social / forum (fortement recommandé)
HIBP_API_KEY=
VIRUSTOTAL_API_KEY=
OTX_API_KEY=
URLSCAN_API_KEY=
IPINFO_API_KEY=
SHODAN_API_KEY=
OSINTGRAPH_PUBLIC_API_URL= # URL HTTPS publique de l’API (recherche image par URL)
```

## Planifié (légal, non implémenté)

| Outil / idée | Statut |
|--------------|--------|
| **PhoneInfoga** (sundowndev) | Plugin local footprint — priorité recommandée |
| **IntelX** | Connecteur `INTELX_API_KEY` (API officielle uniquement) |
| **IntelBase** | API payante analyste — pas de scrape UI |

## Hors périmètre — non intégré volontairement

Ces projets (souvent mentionnés sur **r/OSINT**, **r/osinttools**) ne seront **pas** dupliqués ni embarqués dans OSINTGraph :

| Projet | Raison |
|--------|--------|
| **Telespot** (+ `--dehashed`) | Bases de fuites / credentials (DeHashed) — données volées, pas OSINT « sources ouvertes » documentées |
| **VoidAccess** | Automatisation dark web / Tor, scraping agressif — hors éthique produit |
| **Godseye** | Dark web + extraction automatisée de secrets / creds |
| **Dumps ANTS / BDD pirate** | Accès non autorisé aux registres ; mentions web publiques seulement via transforms existants |
| **Scrape IntelBase / IntelX** | Contournement des CGU — uniquement API officielle + clé analyste si un jour connecteur |

Pour une veille communautaire, voir [REDDIT_OSINT_MAP.md](./REDDIT_OSINT_MAP.md).

## Comportement recherche web (important)

Les transforms `web_search_assistants` / `social_web_search` ajoutent au **graphe** des nœuds = **pages trouvées** (titre, URL, extrait), pas les moteurs de recherche. Le panneau **Transformations** affiche des cartes « Résultats trouvés ». Sans `BRAVE_SEARCH_API_KEY`, les hits peuvent être limités (DDG Instant + Wikipedia).

## Références

- [TRANSFORM_HUB.md](./TRANSFORM_HUB.md) — catalogue et API
- [DEATH_SEARCH.md](./DEATH_SEARCH.md) — décès INSEE
- Règles dépôt : `.cursor/rules/investigation-ethics.mdc`, `AGENTS.md`
