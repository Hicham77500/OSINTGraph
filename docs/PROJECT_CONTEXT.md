# OSINTGraph — Project Context

> Investigation Workspace UX, carnet model, and routing map.  
> See also `.agent/specs/001-domain-model.md` for the full domain model.

## Investigation flow

```
Dossiers list (/)
  └── Dossier (/dossier/:id) — investigation hub
        ├── Full graph (/dossier/:id/graph) — primary entry (hero card on hub)
        ├── Carnet view (/dossier/:id/carnet/:carnetId) — typed list/timeline/notes
        └── Person view (/dossier/:id/person/:entityId) — intelligence profile for a PERSON
```

## Empty dossier user journey

When a dossier has zero stats and no carnet entities, the hub shows a **welcome banner** with a 3-step workflow:

1. **Start with the full graph** — add entities, run transforms, build the network
2. **Use Notes** — quick capture without opening the graph (`+ Nouvelle note` form in the Notes carnet)
3. **Chronologie** — fills automatically as observations are collected via the graph or other carnets

The **Graphe complet** card is visually primary (hero, distinct `GitGraph` icon). Carnets appear below under **Axes d'investigation**, each with a type-specific icon and description subtitle (not only entity count).

## Carnet dependencies

| Carnet | Requires graph? | Empty-state behavior |
|--------|-----------------|----------------------|
| **Graphe complet** | — | Canvas empty state (add from left panel) |
| **Notes** | No | Inline note form always available; creates `CUSTOM` entity + MANUAL observation |
| **Chronologie** | Indirect | Explains timeline builds from graph/carnet observations; CTA → graph |
| **Personnes, Réseaux sociaux, etc.** | Yes (mostly) | Contextual empty state + CTA → graph; Réseaux sociaux also has quick-add username |

## When to use each view

| View | Use when |
|------|----------|
| **Dossier (hub)** | Orienting within an investigation; graph hero + carnet axes |
| **Full graph** | Primary relational workspace — transforms, linking, exploration |
| **Carnet view** | Working within one axis — browse persons, accounts, timeline, notes |
| **Person view** | Deep dive on a single person: identities, social, relations, evidence, AI |

The carnet grid is **kept** as secondary navigation under investigation axes. Each default dossier gets typed carnets (Personnes, Réseaux sociaux, etc.). Breadcrumbs on carnet views: `Mes dossiers > Dossier > Carnet`.

## Carnet purpose (`notebook_type`)

| `notebook_type` | Default name | Shows |
|-----------------|--------------|-------|
| `personnes` | Personnes | Entity list filtered to `PERSON`; cards link to Person view |
| `reseaux_sociaux` | Réseaux sociaux | `SOCIAL_ACCOUNT`, `USERNAME` |
| `entreprises` | Organisations | `ORGANIZATION` |
| `pseudonymes` | Pseudonymes | `ALIAS`, `USERNAME` |
| `chronologie` | Chronologie | Timeline of observations (all entities in carnet) |
| `notes` | Notes | Analyst notes; inline creation via POST entity `CUSTOM` with `{title, content}` |
| `custom` | (user-defined) | Generic entity list for that carnet |

**Note creation API:** `POST /api/v1/dossiers/:id/entities` with `entity_type: CUSTOM`, `carnet_id` set to the Notes carnet, `properties: { title, content }`. Backend adds MANUAL source + label observation + notes observation when `content` is present.

**Note edit/delete:** `PATCH /api/v1/entities/:id` (update `properties`, `label`) and `DELETE /api/v1/entities/:id` (cascade observations/sources). Note cards show `created_at` / `updated_at` and observation `observed_at` when present. Seed marker `__osintgraph_demo_seed_v1__` is hidden from the notes list.

**Dossier trash:** `DELETE /api/v1/dossiers/:id` soft-deletes (`deleted_at`); `GET /api/v1/dossiers/trash`, `POST /api/v1/dossiers/:id/restore`, `DELETE /api/v1/dossiers/:id/permanent`.

Entities are loaded via `GET /api/v1/dossiers/:id/entities?carnet_id=:carnetId`. Client-side filters apply `notebook_type` → allowed `entity_type` values.

## Routing map

| Route | Component | Data |
|-------|-----------|------|
| `/` | `DossiersPage` | Active dossiers (excludes trash) |
| `/trash` | `TrashPage` | Soft-deleted dossiers |
| `/dossier/:dossierId` | `DossierPage` | Carnets for dossier |
| `/dossier/:dossierId/carnet/:carnetId` | `CarnetViewPage` | Entities + observations per carnet type |
| `/dossier/:dossierId/graph` | `CarnetGraphPage` | Legacy graph (`workspace_id` or dossier id) |
| `/dossier/:dossierId/person/:entityId` | `PersonViewPage` | Single PERSON entity |

## API wiring

- `fetchCarnets(dossierId)` — carnet metadata including `notebook_type`
- `fetchEntities(dossierId, carnetId)` — entities scoped to carnet
- Observations for timeline/notes: `GET /api/v1/entities/:id/observations` per entity in carnet

## UI conventions

- Dark Glassmorphism (`DossiersPage.css`, `CarnetViewPage.css`)
- i18n keys under `dossier.*` and `carnetView.*` in `en.ts` / `fr.ts`
- Provenance badges on entity cards: `status`, confidence %
