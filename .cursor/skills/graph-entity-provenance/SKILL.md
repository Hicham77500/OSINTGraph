---
name: graph-entity-provenance
description: Model and implement provenance for OSINTGraph entities — Source, Observation, Evidence, Relation, Hypothesis with confidence statuses. Use when designing data models, APIs, or UI for investigation data.
---

# Graph Entity Provenance

## Chain

```
Source → Observation → Evidence → Relation / Hypothesis
```

## Confidence statuses

Always assign one of: `CONFIRMED`, `LIKELY`, `POSSIBLE`, `UNVERIFIED`, `CONTRADICTED`.

## UI requirements

- Every social account card shows: platform, source method, collectedAt, confidence badge, status
- Relations show evidence count and confidence; click opens side panel with evidence list
- Timeline distinguishes: observed fact, deduced event, AI hypothesis
- AI Analysis section labels all outputs as hypotheses until analyst confirms

## API patterns

- POST entity → auto-create Source + Observation if from transform/import
- POST relation → require at least one evidence_id or create UNVERIFIED with warning
- GET `/api/v1/entities/:id/evidence` — filter by platform, date, confidence, status

## Entity resolution

- Engine produces `MergeSuggestion` with similarity + reasons
- Never auto-merge PERSON entities
- Merge action writes AuditEvent and is reversible via audit history

## Spec reference

Full model: `.agent/specs/001-domain-model.md`

## Migration from legacy nodes

When importing blob nodes:

```python
status = "UNVERIFIED"
collection_method = metadata.get("source", "manual") → map to IMPORT or MANUAL
confidence = metadata.get("confidence", 100) / 100.0
```
