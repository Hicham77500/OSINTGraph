# Transform Hub (Maltego Data Hub parity)

OSINTGraph exposes a **partner catalog** inspired by the Maltego Data Hub UI. We do **not** ship proprietary Maltego transforms; each entry maps to:

- an **installed plugin** under `backend/plugins/` (runnable from the graph inspector), or
- a **planned** integration (commercial partner API, ethics review, or stub).

## API

- `GET /transforms` — installed plugins, with `env_keys`, `requires_api_key`, `configured`.
- `GET /transforms/hub` — full catalog from `backend/config/transform_hub_catalog.json` merged with install status.

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

## Ethics

- No demo breach data when HIBP key is missing.
- Commercial Maltego Data Pass modules remain **planned** until an analyst-owned API contract exists.
- All transform output keeps provenance via `observations` and confidence statuses.

## Extending the catalog

Edit `backend/config/transform_hub_catalog.json` and add a matching plugin under `backend/plugins/` when implementing a partner. Re-run `pytest backend/tests/test_plugins.py`.
