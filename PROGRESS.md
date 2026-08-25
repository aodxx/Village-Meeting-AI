# Progress — Village Meeting AI

Last updated: 2026-08-26

## Current Phase

**Phase 0 — Product Foundation**

## Completed

- [x] Product concept defined
- [x] Target use case clarified as village/community meetings
- [x] User requirement interview completed for V1 direction
- [x] Screen-by-screen UX architecture defined
- [x] Human-in-the-loop rule for resolutions defined
- [x] Public full-report sharing direction defined
- [x] Audio deletion policy defined
- [x] PRD V1 created
- [x] Initial technical architecture created
- [x] Initial Google Sheets data model created
- [x] Implementation roadmap created

## Important Product Decisions

1. Public readers do not need to login.
2. Public readers can read the full final report, download PDF, and share the link.
3. Attendance/member management is not part of V1.
4. Speaker identity in V1 is generic: Speaker 1 / Speaker 2 / Speaker 3.
5. AI proposes possible resolutions; humans confirm them.
6. AI should identify follow-up work and responsible parties only when supported by the transcript.
7. Agenda can be provided before the meeting or inferred by AI afterward.
8. Transcription can be live or post-meeting.
9. Audio should be deletable only after transcript, AI processing, and final report are safely completed.
10. PDF visual direction is Modern + Formal, not a rigid legacy government form.

## Current Repository Foundation

Expected core documents:

- `README.md`
- `PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA-MODEL.md`
- `docs/API-CONTRACT.md`
- `docs/UX-FLOW.md`
- `ROADMAP.md`
- `PROGRESS.md`
- `CONTRIBUTING.md`
- `AGENTS.md`

## Next Step

### Phase 0.1 — Technical Spike

Before building the UI, verify the most technically risky part first:

**Can the selected speech-to-text path reliably handle long Thai village meetings (target 1–3 hours), speaker separation, timestamps, and reasonable cost?**

The spike should test:

- Thai speech quality
- Multiple speakers
- Background noise
- Long audio duration
- File/chunk limits
- Processing time
- Apps Script orchestration limits
- Retry behavior
- Cost estimate

## Do Not Start Yet

Avoid building a large UI or PDF system before the transcription architecture is validated. The recording/transcription path is the highest-risk dependency and could force architectural changes.

## Definition of Phase 0 Done

Phase 0 is complete when:

- [ ] API contract is finalized
- [ ] Speech-to-text provider/approach is selected
- [ ] Long-meeting technical spike passes
- [ ] Frontend stack is selected
- [ ] Deployment approach is selected
- [ ] Repository structure for code is initialized

## Development Note

Any AI agent or developer starting work should read in this order:

1. `README.md`
2. `PRD.md`
3. `PROGRESS.md`
4. `ROADMAP.md`
5. `docs/ARCHITECTURE.md`
6. `docs/DATA-MODEL.md`
7. `docs/API-CONTRACT.md`
8. `docs/UX-FLOW.md`
9. `AGENTS.md`
