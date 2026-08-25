# Free STT Policy — Village Meeting AI

## Product Decision

Village Meeting AI V1 must not require the user to pay recurring Speech-to-Text service fees.

The implementation may use **any technical approach** as long as normal use of the project does not require a paid STT subscription or paid per-minute/per-hour transcription API.

## Allowed Approaches

AI agents and developers may choose or combine:

- Open-source Speech-to-Text models
- Local/on-device transcription
- Browser-based transcription where practical
- Self-hosted transcription
- Free cloud compute or free notebook environments where appropriate
- Free-tier APIs, only when they can be used without mandatory billing for the intended V1 workflow
- Hybrid pipelines
- Chunked processing
- Post-meeting transcription
- Optional live preview transcription
- Any other zero-service-fee approach that meets the product requirements

No provider is preferred or locked in.

## Not Allowed as a Required V1 Dependency

The default V1 workflow must not require:

- paid Azure Speech usage
- paid Google Cloud Speech-to-Text usage
- paid Amazon Transcribe usage
- paid OpenAI transcription usage
- paid Groq transcription usage
- paid AssemblyAI usage
- or any other metered STT service that creates a required recurring transcription bill

These services may only be documented as optional future alternatives, not as a mandatory V1 dependency.

## Priority Order

When evaluating a transcription approach, optimize in this order:

1. Zero required STT service fee
2. Thai transcription quality sufficient for meeting reports
3. Reliability for long meetings
4. Ease of setup and maintenance
5. Timestamp support
6. Speaker separation if available
7. Live transcription

Speaker diarization is **not a blocker** for V1. Generic speaker labels are desirable but may be omitted if they force the project onto a paid service.

## Important Product Principle

The purpose of transcription is to create a trustworthy draft for AI-assisted village meeting reports.

The system does not need court-grade verbatim transcripts or perfect speaker identity.

If a free approach produces good Thai text but cannot reliably identify speakers, V1 should prefer the free approach and retain human review before final report publication.

## Cost Guard

AI agents must not silently introduce a paid dependency.

Before adding any external service, verify whether it can incur charges. If billing is required for the intended workflow, it cannot become the default V1 transcription path without an explicit product decision changing this policy.

## Architecture

The Speech-to-Text layer must remain provider-neutral so the project can swap between local, browser, open-source, free-tier, or future paid providers without changing the report layer.
