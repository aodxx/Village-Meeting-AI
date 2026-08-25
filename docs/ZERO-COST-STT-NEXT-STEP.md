# Zero-Cost STT — Next Step

The previous Azure-first recommendation has been superseded by the product requirement that normal V1 usage must not require paid Speech-to-Text service fees.

## New Objective

Find the best practical transcription approach for long Thai village meetings while keeping required transcription service cost at zero.

## Agent Freedom

The implementation is not restricted to any provider or architecture. It may use:

- open-source STT models
- local or on-device processing
- browser/WebAssembly/WebGPU processing
- self-hosted processing
- free compute environments
- free-tier services that can support the intended V1 workflow without mandatory paid usage
- hybrid approaches
- chunked post-meeting transcription

The agent may propose another approach if it better satisfies the objective.

## V1 Trade-off

Speaker diarization and live transcription are secondary. They may be reduced or omitted if they force the project onto paid infrastructure.

The required outcome is high-enough-quality Thai text for a human-reviewed meeting report.

## Required Experiment

Before large UI implementation, build and document at least one end-to-end zero-service-fee transcription prototype and benchmark it against representative Thai meeting audio.

Record:

- Thai text quality
- long-audio strategy
- processing time
- required hardware/compute
- timestamp availability
- speaker separation availability
- failure/retry behavior
- operational steps
- whether any billing account or metered paid service is required

A solution fails the V1 cost gate if normal operation requires paid STT usage.
