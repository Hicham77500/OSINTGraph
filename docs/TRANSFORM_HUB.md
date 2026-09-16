# Transform Hub (Maltego Data Hub parity)

OSINTGraph exposes a **partner catalog** inspired by the Maltego Data Hub UI. We do **not** ship proprietary Maltego transforms; each entry maps to:

- an **installed plugin** under `backend/plugins/` (runnable from the graph inspector), or
- a **planned** integration (commercial partner API, ethics review, or stub).

## API

- `GET /transforms` — installed plugins, with `env_keys`, `requires_api_key`, `configured`.
- `GET /transforms/hub` — full catalog from `backend/config/transform_hub_catalog.json` merged with install status.
- `GET /transforms/api-keys` — signup and documentation URLs from `backend/config/api_providers.json` (shown in the UI via the **i** info control).

## UI

On the investigation graph (`/dossier/:id/graph`), use **Transform hub** in the top bar to browse partners, filter installed vs planned, and see missing API keys.

## New plugins (public / official APIs)

| Plugin | Input | Env var |
|--------|-------|---------|
| `hibp_lookup` | EMAIL | `HIBP_API_KEY` |
| `crtsh_lookup` | DOMAIN | — |
| `urlscan_lookup` | DOMAIN, URL | `URLSCAN_API_KEY` (recommended) |
| `virustotal_lookup` | DOMAIN, IP | `VIRUSTOTAL_API_KEY` |
| `otx_lookup` | DOMAIN, IP | `OTX_API_KEY` |
| `ipinfo_lookup` | IP | `IPINFO_API_KEY` (optional free tier) |

## General search (web, social, forums, phone, plate)

- UI: toolbar **Web & social search** or transforms on person/username/email/phone/plate nodes.
- `GET /api/v1/investigation/general-search?q=…&mode=web|person|social|forum|phone|plate&keywords=…&fetch=true` — with `fetch=true`, returns `result_cards` (real URLs/snippets).
- Plugins: `web_search_assistants`, `social_web_search`, `forum_search_assistants`, `vehicle_plate_search`.
- **Graph nodes = pages found**, not search-engine names. Inspector shows **Résultats trouvés** cards after a transform.
- **`BRAVE_SEARCH_API_KEY`** strongly recommended for person/social/forum hit quality ([Brave Search API](https://brave.com/search/api/)).
- Forum keywords (e.g. `reddit`, `leak`, `pirate`) are **analyst-selected** — public index only, no private forum bypass.
- **Sherlock / Maigret / Holehe** remain the automated username/email transforms.

See also [OSINT_TOOLS_SCOPE.md](./OSINT_TOOLS_SCOPE.md) and [REDDIT_OSINT_MAP.md](./REDDIT_OSINT_MAP.md).

## Visual investigation (images)

- UI: toolbar **Visual search** or person / location inspector.
- `POST /api/v1/investigation/visual-search/upload` stores analyst images locally; assistants link to Google Lens, Bing, Yandex, TinEye.
- Google cannot be embedded in an iframe — analysts open official UIs and document findings manually (provenance required).
- Set `OSINTGRAPH_PUBLIC_API_URL` when the API is reachable on the public internet for URL-based reverse search links.

## Ethics

- No demo breach data when HIBP key is missing.
- **Not integrated:** Telespot/DeHashed, VoidAccess, Godseye, stolen registry dumps, scrape of IntelBase/IntelX UIs.
- Commercial Maltego Data Pass modules remain **planned** until an analyst-owned API contract exists.
- All transform output keeps provenance via `observations` and confidence statuses (default **UNVERIFIED** for web hits).

## Extending the catalog

Edit `backend/config/transform_hub_catalog.json` and add a matching plugin under `backend/plugins/` when implementing a partner. Re-run `pytest backend/tests/test_plugins.py`.
