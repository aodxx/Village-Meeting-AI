# Roadmap — Village Meeting AI

## Phase 0 — Product Foundation

Status: **In progress**

- [x] Define product vision
- [x] Define V1 scope
- [x] Define user flow
- [x] Define screen architecture
- [x] Define initial technical architecture
- [x] Define Google Sheets data model
- [ ] Finalize API contract
- [ ] Validate speech-to-text approach for long Thai meetings
- [ ] Decide frontend stack and deployment path

Phase 0.1 status: **Zero-STT-fee local Thai STT worker prototype validated end-to-end.** The local worker is the primary candidate for POST mode; paid providers including Azure Speech Batch Standard are fallback-only. An authorized Thai multi-speaker/noise/1–3 hour benchmark remains required before production confirmation.

Exit criteria: local STT plumbing, normalized contract, zero-STT-fee policy, and adapter boundary are documented and smoke-tested; real-meeting quality, long-audio resource, diarization, and restart/retry gates remain before Phase 3 production implementation.

## Phase 1 — App Foundation

- [ ] Create PWA shell
- [ ] Bottom navigation
- [ ] Home screen
- [ ] Create Meeting screen
- [ ] Agenda editor
- [ ] Meeting history
- [ ] Settings
- [ ] Apps Script health endpoint
- [ ] Google Sheets bootstrap/setup
- [ ] Google Drive folder bootstrap

Exit criteria: user can create and reopen a meeting record end-to-end without audio or AI.

## Phase 2 — Recording

- [ ] Microphone permission UX
- [ ] Start/Stop recording
- [ ] Pause/Resume
- [ ] Timer
- [ ] Audio level/waveform
- [ ] Important marker
- [ ] Upload/storage lifecycle
- [ ] End-meeting confirmation

Exit criteria: a real meeting audio recording can be captured and safely associated with a MeetingID.

## Phase 3 — Transcription

- [ ] Speech-to-text adapter
- [ ] Thai transcription
- [ ] Speaker separation
- [ ] Transcript segmentation with timestamps
- [ ] Transcript screen
- [ ] Important marker highlighting
- [ ] Retry/error handling

Exit criteria: a recorded meeting produces a usable speaker-separated transcript.

## Phase 4 — AI Meeting Analysis

- [ ] Gemini structured output schema
- [ ] Agenda matching/generation
- [ ] Agenda summaries
- [ ] Discussion summary
- [ ] Possible resolution detection
- [ ] Evidence timestamps
- [ ] Follow-up extraction
- [ ] Responsible party extraction
- [ ] Due date extraction
- [ ] AI output validation

Exit criteria: AI review data is structured, grounded in transcript, and safe for human review.

## Phase 5 — Human Review

- [ ] AI Review screen
- [ ] Confirm resolution
- [ ] Edit resolution
- [ ] Reject resolution
- [ ] Edit follow-up items
- [ ] Generate draft report
- [ ] Draft report editor

Exit criteria: human can correct AI output before any final document is created.

## Phase 6 — Final Report & PDF

- [ ] Final snapshot
- [ ] Report versioning
- [ ] Modern + Formal A4 template
- [ ] PDF generation
- [ ] PDF storage
- [ ] Download PDF

Exit criteria: a reviewed meeting can produce a stable final PDF.

## Phase 7 — Public Publishing

- [ ] Public slug
- [ ] Public report page
- [ ] No-login access
- [ ] Share link
- [ ] Public PDF download
- [ ] Prevent draft/internal data leakage

Exit criteria: a final report can be safely shared with villagers through a public URL.

## Phase 8 — Audio Cleanup & Reliability

- [ ] Eligibility check before audio delete
- [ ] User confirmation
- [ ] Drive deletion
- [ ] AudioDeletedAt audit field
- [ ] Processing retry flow
- [ ] Error states
- [ ] Long-meeting test
- [ ] Mobile test

Exit criteria: the complete workflow is reliable for real village meetings.

## V1 Release Gate

V1 is complete only after a real meeting test succeeds from recording through public report publication.

## Future / V2

Not part of V1:

- AI meeting search
- Ask Meeting AI
- Resolution tracker
- Village project tracker
- LINE integration
- Meeting statistics
- Member accounts
- Online voting
- Voice identity
