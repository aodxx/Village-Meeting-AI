# AI Agent Instructions — Village Meeting AI

This file defines the operating rules for AI coding agents working in this repository.

## Mission

Build a mobile-first AI assistant for village/community meetings that can record, transcribe, structure, review, finalize, and publish meeting reports.

## Read Order

Before changing code or architecture, read:

1. `README.md`
2. `PRD.md`
3. `PROGRESS.md`
4. `ROADMAP.md`
5. `docs/ARCHITECTURE.md`
6. `docs/DATA-MODEL.md`
7. `docs/API-CONTRACT.md`
8. `docs/UX-FLOW.md`
9. `docs/FREE-STT-POLICY.md`

## Non-Negotiable Product Rules

1. AI may propose a resolution, but only a human can confirm it.
2. AI must not invent responsible parties, dates, resolutions, or facts not supported by the transcript.
3. Final reports must be snapshots and must not silently change when draft data changes.
4. Public report views must never expose draft/internal/private metadata.
5. Audio deletion is allowed only after transcription, AI processing, and final report completion, plus explicit user confirmation.
6. V1 public readers do not need accounts.
7. V1 does not require voice identity or paid speaker diarization.
8. Avoid adding V2 features unless explicitly requested.
9. V1 must not require a paid Speech-to-Text service. The agent may use any zero-service-fee technical approach that satisfies `docs/FREE-STT-POLICY.md`.

## Google Drive Project Root

Use this existing Drive folder as the single project root for project-created Drive content:

- Folder name: `VillageMeetingAI`
- Folder ID: `1IEUaLmKAJqgpJaD8jsfdfnda9CmOWODY`

Do not create another Drive project root. Create subfolders only when needed and keep test data separate from real meeting data.

## Engineering Rules

- Never commit API keys, OAuth tokens, service credentials, or private meeting data.
- Never silently introduce a paid STT dependency.
- Use stable string IDs. Never expose Sheet row numbers as IDs.
- Keep speech-to-text behind a provider/engine adapter.
- Validate all AI structured output before persistence.
- Make processing actions safe to retry where practical.
- Enforce meeting state transitions in the backend.
- Keep public endpoints read-only.
- Prefer simple, maintainable solutions over unnecessary abstractions.

## Current Priority

The project is currently in Phase 0.

The highest-risk technical question is finding a **zero-required-service-fee** transcription path that is good enough for long Thai village meetings.

Do not optimize for a commercial STT provider. Test free/open-source/local/browser/free-tier approaches first.

Do not invest heavily in UI implementation before the transcription technical spike is resolved.

## Change Workflow

For every meaningful implementation change:

1. Inspect current relevant code/docs.
2. Implement the smallest coherent change.
3. Run available tests/build/checks.
4. Fix failures before considering the task complete.
5. Update `PROGRESS.md` when a milestone changes.
6. Update architecture/data/API docs when contracts change.

## Scope Protection

V1 does not include:

- attendance/member management
- OTP/login for villagers
- online voting
- voice identity
- face recognition
- AI search/chat
- comments
- full task-management system
- multi-step approval workflow
- LINE login
- native Android/iOS apps

If a requested change conflicts with these boundaries, document the product decision before implementing it.

## Definition of Good AI Output

AI-derived meeting data should be:

- traceable to transcript evidence where possible
- structured
- editable by the human recorder
- explicit about unknown values
- safe to reject or retry

Prefer `null` / `ยังไม่ระบุ` over guessing.
