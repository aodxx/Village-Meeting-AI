# Contributing — Village Meeting AI

## Before You Start

Read these files first:

1. `README.md`
2. `PRD.md`
3. `PROGRESS.md`
4. `ROADMAP.md`
5. `docs/ARCHITECTURE.md`
6. `docs/DATA-MODEL.md`
7. `docs/API-CONTRACT.md`
8. `docs/UX-FLOW.md`
9. `AGENTS.md`

## Development Principles

- Keep V1 scope small and practical.
- Do not add features listed under Non-Goals without an explicit product decision.
- Human review is mandatory for resolutions and final reports.
- AI must not invent missing facts.
- Use stable IDs, never Sheet row numbers as public/entity IDs.
- Do not commit secrets, API keys, tokens, or private meeting data.
- Public report endpoints must be read-only.
- Keep speech-to-text behind an adapter so providers can change.

## Suggested Code Structure

When implementation begins:

```text
/
  frontend/
    src/
    public/
  appsscript/
  docs/
  tests/
  README.md
  PRD.md
  ROADMAP.md
  PROGRESS.md
  AGENTS.md
```

The exact frontend framework can be selected after Phase 0 technical decisions.

## Branch / Commit Guidance

Use small, understandable commits.

Examples:

- `feat: add meeting creation flow`
- `feat: add important marker`
- `fix: prevent invalid meeting state transition`
- `docs: update transcription architecture`
- `test: cover report finalization guard`

## Testing Expectations

Each implemented feature should include the smallest meaningful validation possible.

Critical flows that require tests:

- meeting state transitions
- resolution confirmation rules
- final report snapshot
- audio deletion guard
- AI structured-output validation
- public report data filtering

## Documentation Rule

When a technical/product decision changes:

- update the relevant document
- update `PROGRESS.md`
- update `ROADMAP.md` when phase scope/status changes

Do not leave documentation describing an architecture that no longer exists.

## Pull Request Checklist

- [ ] Change matches PRD V1
- [ ] No secrets committed
- [ ] Tests/build pass when available
- [ ] Data model/API contract updated if needed
- [ ] Public data exposure reviewed
- [ ] PROGRESS.md updated for meaningful milestones
