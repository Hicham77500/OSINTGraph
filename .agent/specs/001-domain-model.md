# Spec 001 — Modèle de domaine OSINTGraph

> Version 1.0 — juillet 2026

## Vue d'ensemble

```
Dossier
  └── Carnet[]
        └── Entité[]
              ├── Source[]
              │     └── Observation[]
              ├── Evidence[] (liée à observations / relations / hypothèses)
              ├── Relation[] (vers autres entités)
              └── Hypothesis[] (interprétations, dont sorties IA)
```

## Dossier

Représente une investigation.

| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | Identifiant |
| name | string | Nom affiché |
| description | string? | Contexte |
| workspace_id | string? | Alias legacy (migration) |
| created_at | datetime | |
| updated_at | datetime | |

## Carnet

Axe d'investigation au sein d'un dossier.

| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | |
| dossier_id | UUID | Parent |
| name | string | Ex: "Personnes", "Réseaux sociaux" |
| notebook_type | enum | personnes, reseaux_sociaux, entreprises, pseudonymes, telephones, emails, domaines, evenements, chronologie, notes, custom |
| created_at | datetime | |

L'utilisateur peut créer des carnets custom (`notebook_type: custom`).

## Entité

Élément observable.

| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | |
| dossier_id | UUID | |
| carnet_id | UUID? | |
| entity_type | enum | PERSON, ORGANIZATION, ALIAS, USERNAME, SOCIAL_ACCOUNT, EMAIL, PHONE, DOMAIN, WEBSITE, LOCATION, EVENT, DOCUMENT, MEDIA, CUSTOM |
| label | string | Identifiant principal |
| properties | JSON | Champs typés selon entity_type |
| confidence | float 0-1 | Confiance globale |
| status | ConfidenceStatus | |
| created_at / updated_at | datetime | |

### Person (entité enrichie)

`entity_type: PERSON` avec properties :

```json
{
  "first_name": "string?",
  "last_name": "string?",
  "aliases": ["string"],
  "notes": "string?"
}
```

## Source

Origine de l'information.

| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | |
| entity_id | UUID | Entité observée |
| platform | string | instagram, tiktok, manual, dns, etc. |
| url | string? | URL publique |
| collection_method | enum | MANUAL, PUBLIC_SEARCH, OFFICIAL_API, IMPORT, TRANSFORM |
| collected_at | datetime | |
| metadata | JSON? | |

## Observation

Fait directement observé.

| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | |
| source_id | UUID | |
| entity_id | UUID | |
| content | JSON | Donnée observée |
| observed_at | datetime | |
| confidence | float | |
| status | ConfidenceStatus | |

Exemple content :

```json
{
  "field": "username",
  "value": "example123",
  "platform": "instagram"
}
```

## Evidence

Élément supportant une relation ou hypothèse.

| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | |
| observation_id | UUID? | |
| relation_id | UUID? | |
| hypothesis_id | UUID? | |
| summary | string | |
| confidence | float | |
| status | ConfidenceStatus | |

## Relation

Lien entre deux entités.

| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | |
| dossier_id | UUID | |
| source_entity_id | UUID | |
| target_entity_id | UUID | |
| relation_type | enum | USES, KNOWS, FOLLOWS, WORKS_AT, MEMBER_OF, OWNS, CREATED, MENTIONED_BY, LOCATED_AT, RELATED_TO, RESOLVES_TO, LINKED_TO |
| confidence | float | |
| status | ConfidenceStatus | |
| evidence_ids | UUID[] | |

## Hypothesis

Interprétation non confirmée (y compris IA).

| Champ | Type | Description |
|-------|------|-------------|
| id | UUID | |
| dossier_id | UUID | |
| entity_id | UUID? | |
| claim | string | |
| reasoning_summary | string | |
| evidence_ids | UUID[] | |
| confidence | float | |
| contradictions | string[] | |
| status | ConfidenceStatus | |
| source | enum | ANALYST, AI, SYSTEM |
| analyst_action | enum? | CONFIRMED, REJECTED, NEEDS_REVIEW |

## ConfidenceStatus

```
CONFIRMED | LIKELY | POSSIBLE | UNVERIFIED | CONTRADICTED
```

## AuditEvent

Traçabilité append-only.

| Champ | Type |
|-------|------|
| id | UUID |
| actor | string (user id or "system") |
| action | string (ENTITY_CREATED, RELATION_CONFIRMED, MERGE_SUGGESTION_REJECTED, ...) |
| entity_type | string |
| entity_id | UUID |
| previous_state | JSON? |
| new_state | JSON? |
| timestamp | datetime |

## MergeSuggestion (Entity Resolution)

| Champ | Type |
|-------|------|
| id | UUID |
| entity_a_id | UUID |
| entity_b_id | UUID |
| similarity | float |
| reasons | string[] |
| status | PENDING, MERGED, REJECTED |

**Jamais de fusion automatique** — action analyste requise.

## Context Readiness Score

Score 0-100 calculé avant analyse IA :

- nombre de sources indépendantes
- nombre d'observations
- qualité des sources
- plateformes distinctes
- identifiants concordants
- contradictions détectées

Seuil par défaut : 60. En dessous : message « Données insuffisantes ».

## PlatformConnector

```python
class PlatformConnector:
    platform: str
    capabilities: list[str]  # MANUAL, PUBLIC_SEARCH, OFFICIAL_API, IMPORT
    async def normalize(self, raw: dict) -> dict: ...
    async def search(self, query: str) -> list: ...
    async def parse(self, url: str) -> dict: ...
    async def build_observations(self, parsed: dict) -> list: ...
```

## Migration legacy

1. `workspace_id` → dossier avec même id
2. Chaque node blob → entité `UNVERIFIED` + observation `IMPORT`
3. Chaque edge blob → relation `RELATED_TO`
4. Blob graph conservé en dual-write jusqu'à stabilisation
