# Progress — Village Meeting AI

Last updated: 2026-08-26

## Current Phase

**Phase 0 — Product Foundation / Phase 0.1 Zero-Cost STT Technical Spike**

Status: **Commercial-provider recommendation superseded; zero-service-fee transcription approach required**

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
- [x] Initial commercial STT provider research completed
- [x] Provider-neutral STT adapter and asynchronous orchestration design completed
- [x] Initial STT Technical Spike document created
- [x] Zero-cost STT product policy added in `docs/FREE-STT-POLICY.md`
- [x] Zero-cost next-step brief added in `docs/ZERO-COST-STT-NEXT-STEP.md`
- [x] Azure-first recommendation removed from the active V1 direction
- [x] Free/open-source candidate shortlist researched and documented
- [x] Local Thai STT prototype runs end-to-end with zero STT service fee
- [x] Smoke-test result and evaluator committed under `tools/free_stt_spike/`

## Important Product Decisions

1. Public readers do not need to login.
2. Public readers can read the full final report, download PDF, and share the link.
3. Attendance/member management is not part of V1.
4. Voice identity is not required in V1.
5. Speaker diarization is optional and must not force use of a paid service.
6. AI proposes possible resolutions; humans confirm them.
7. AI should identify follow-up work and responsible parties only when supported by the transcript.
8. Agenda can be provided before the meeting or inferred by AI afterward.
9. Transcription can be live or post-meeting, but live mode may be reduced or deferred if it conflicts with the zero-cost requirement.
10. Audio should be deletable only after transcript, AI processing, and final report are safely completed.
11. PDF visual direction is Modern + Formal, not a rigid legacy government form.
12. **V1 must not require a paid Speech-to-Text service.**
13. AI agents may use any technical approach—open source, local, browser, self-hosted, free compute, free tier, chunking, or hybrid—as long as normal V1 use does not require transcription service fees.
14. Commercial metered STT services are not mandatory/default V1 dependencies. They may remain optional future alternatives only.

## Superseded Decision

The earlier recommendation to use Azure Speech Batch Standard as the primary POST transcription provider is **no longer the product direction**.

That research remains useful as a comparison baseline only.

## Next Step

### Phase 0.1 — Zero-Cost STT Technical Spike

Find and empirically test the best practical transcription architecture that requires **no paid STT service for normal V1 operation**.

Candidate families may include, but are not limited to:

- Whisper / faster-whisper or other open-source STT
- Local/on-device processing
- Browser/WebAssembly/WebGPU processing
- Self-hosted lightweight processing
- Free notebook/compute approaches where operationally practical
- Truly usable free-tier APIs that do not require mandatory paid usage for V1
- Hybrid processing

The agent is not restricted to this list.

## Benchmark Questions

The spike should answer:

- Is Thai transcription good enough to create a correct meeting-report draft?
- Can it handle a real 1–3 hour meeting, directly or through chunking?
- What device/server resources are required?
- Can users operate it without a paid transcription bill?
- How long does processing take?
- How are failures/retries handled?
- Are timestamps available?
- Is speaker separation available for free? If not, can V1 work without it?
- Can the output feed the existing Gemini/report-analysis layer safely?

## Do Not Start Yet

Avoid building a large UI or PDF system before a viable zero-cost transcription path has been proven.

## Phase 0.1 Deliverables

- [x] Initial paid-provider comparison preserved for reference
- [x] Provider-neutral adapter boundary documented
- [x] Zero-cost STT policy documented
- [x] Free/open-source candidate shortlist researched
- [x] At least one zero-service-fee prototype runs end-to-end
- [ ] Authorized Thai audio benchmark completed
- [ ] 1-hour test completed
- [ ] Long-meeting/chunking path demonstrated
- [x] Initial CPU processing time and model/runtime requirements recorded; full resource benchmark remains open
- [x] Local Thai STT worker selected as the Phase 0.1 implementation candidate; production quality confirmation remains open

## Phase 0.1 Continuation Result

The committed E2E smoke test uses the Thai-specific `biodatlab/distill-whisper-th-small` model for transcription, `faster-whisper` base with VAD for speech boundaries, and deterministic pitch-feature clustering for generic labels. It runs locally on CPU without a paid STT service call. On the synthetic Thai fixture of approximately 38.4 seconds, the clean run took approximately 43.963 seconds and produced four normalized segments. The evaluator passed zero STT fee, Thai detection, timestamp/schema validation, and speaker pattern `1,2,1,2`; the average CER proxy was `0.1611`.

This result proves local pipeline plumbing only. It does not close the real-meeting quality gate because the fixture is synthetic, the speaker method is a baseline rather than trained diarization, and no 1-hour/3-hour or authorized real-audio benchmark has been completed. The next step is the real-audio benchmark and long-audio resource/restart test described in `docs/ZERO-COST-STT-NEXT-STEP.md`; no large UI should start before that gate is addressed.

## Definition of Phase 0 Done

Phase 0 is complete when:

- [ ] API contract is finalized
- [ ] Zero-cost speech-to-text approach is selected
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
9. `docs/FREE-STT-POLICY.md`
10. `docs/ZERO-COST-STT-NEXT-STEP.md`
11. `AGENTS.md`
