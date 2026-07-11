---
name: investigation-ethics
description: Legal and ethical constraints for OSINTGraph features. Use before implementing connectors, scrapers, transforms, or AI analysis that touches personal data.
---

# Investigation Ethics

OSINTGraph works only on legally accessible data.

## Never implement

- Authentication bypass or session theft
- Access to private or locked accounts
- Credential stuffing
- Platform protection bypass
- Automated stalking
- Deanonymization presented as certainty without public evidence

## Connector design

Each connector declares `capabilities`:

- `MANUAL` — analyst-entered data
- `IMPORT` — analyst-owned file
- `PUBLIC_SEARCH` — legally accessible public pages only
- `OFFICIAL_API` — documented API with user credentials

Display acquisition method in UI. Do not simulate missing capabilities.

## AI rules

- AI is copilot, never source of truth
- Output structure: claim, reasoning_summary, evidence_ids, confidence, contradictions, status
- Require Context Readiness Score before analysis
- Analyst actions: Confirm, Reject, Mark for review

## Data uncertainty

Sensitive claims keep uncertainty level. Hypotheses ≠ facts.

## Logging

Do not log PII, tokens, or full API responses containing credentials.
