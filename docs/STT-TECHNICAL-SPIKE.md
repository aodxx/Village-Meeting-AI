# STT Technical Spike — Thai Village Meetings

**Phase:** 0.1 Technical Spike

**วันที่:** 2026-08-26

**สถานะ:** Previous commercial-provider recommendation archived; zero-cost STT direction now takes priority

## Product Decision Override

The earlier Azure-first recommendation is no longer the product direction for Village Meeting AI V1.

V1 now requires that normal Speech-to-Text operation **must not require a paid transcription service fee**.

This document remains as research history and a comparison baseline, but all provider recommendations in earlier versions are superseded by:

- `docs/FREE-STT-POLICY.md`
- `docs/ZERO-COST-STT-NEXT-STEP.md`

## New Technical Goal

The team and AI agents may choose **any technical approach** that can produce Thai transcript text good enough for a human-reviewed village meeting report while keeping required STT service cost at zero.

Allowed solution families include:

- Whisper / faster-whisper or other open-source STT models
- local/on-device processing
- browser/WebAssembly/WebGPU processing
- self-hosted processing
- free compute/notebook environments where practical
- genuinely usable free-tier services
- chunked processing
- hybrid pipelines

The agent is not restricted to this list.

## Relaxed V1 Constraints

To keep the project free to operate:

1. Speaker diarization is optional.
2. Generic `SPEAKER_1`, `SPEAKER_2` labels are no longer mandatory if they require a paid service.
3. Live transcription may be deferred or treated as optional.
4. Post-meeting transcription is acceptable.
5. Long recordings may be split into chunks.
6. Processing may take longer than commercial cloud STT if the workflow remains practical.
7. Human review remains mandatory before Final Report publication.

## What Must Still Work

A valid V1 transcription path must provide enough information to support:

- Thai transcript text
- chronological ordering
- timestamps where practical
- agenda extraction
- summary generation
- possible resolution detection
- follow-up extraction
- human review
- final report generation

## Zero-Cost Benchmark Gate

Before large UI implementation, the project must prove at least one zero-service-fee path end-to-end.

The benchmark should record:

- Thai transcription quality
- background-noise behavior
- long meeting strategy (1–3 hours)
- chunking behavior if used
- processing time
- device/server/compute requirements
- timestamps
- optional speaker separation
- failure/retry behavior
- setup complexity
- whether any billing account or metered paid transcription service is required

## Commercial Providers

Azure Speech, Google Cloud Speech-to-Text, Amazon Transcribe, OpenAI transcription, Groq, AssemblyAI, and similar metered providers may remain documented as optional future alternatives or comparison baselines.

They must not be the required/default V1 transcription path unless the product owner explicitly changes the zero-cost policy.

## Current Recommendation

Do **not** choose a commercial provider yet.

The next engineering task is to prototype and benchmark a zero-cost/open-source path first, preserving the existing provider-neutral STT adapter so the implementation can change later without affecting the report layer.
