---
name: code-review-osintgraph
description: Multi-layer code review checklist for OSINTGraph FastAPI + React/TypeScript stack. Use when reviewing PRs or auditing changes in this repository.
---

# OSINTGraph Code Review

Adapted from awesome-skills/code-review-skill for this project's stack.

## Architecture

- [ ] Change is minimal and focused
- [ ] Reuses existing patterns (Zustand, `@register`, PlatformConnector)
- [ ] No premature abstraction
- [ ] Legacy `/graph` API still works if domain API added

## Backend (FastAPI / Python)

- [ ] Type hints on public functions
- [ ] Uses `logging`, not `print`; no PII in logs
- [ ] Transform returns include `observations` with provenance
- [ ] New v1 endpoints use correct HTTP status codes
- [ ] Rate limiting respected on transform endpoints
- [ ] Audit events for CREATE/UPDATE/DELETE/MERGE/CONFIRM/REJECT

## Frontend (React / TS)

- [ ] i18n keys added for new UI strings (en + fr)
- [ ] No unnecessary `any`
- [ ] Provenance/confidence visible on entity cards
- [ ] AI outputs labeled as hypotheses
- [ ] Graph filters accessible (not color-only)

## Security

- [ ] No auth bypass or illegal data collection
- [ ] Input validation on API
- [ ] Secrets in env only, not committed
- [ ] Electron IPC unchanged unless necessary; contextIsolation preserved

## OSINT / Ethics

- [ ] Connector capabilities honestly declared
- [ ] No fake data when API keys missing
- [ ] Entity resolution never auto-merges persons

## Tests

- [ ] pytest for backend changes
- [ ] vitest for store/component changes
- [ ] Smoke test passes

## Upstream

Full modular skill: https://github.com/awesome-skills/code-review-skill
