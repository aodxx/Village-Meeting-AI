# API Contract — Village Meeting AI

## Response Envelope

Success:

```json
{"ok":true,"data":{},"error":null}
```

Failure:

```json
{"ok":false,"data":null,"error":{"code":"ERROR_CODE","message":"Readable message"}}
```

## Core Actions

### System
- `health`

### Meetings
- `createMeeting`
- `getMeeting`
- `listMeetings`
- `startMeeting`
- `endMeeting`

### Agenda
- `saveAgendas`

### Recording
- `addImportantMarker`
- `registerAudio`
- `deleteAudio`

### Processing
- `processMeeting`
- `getProcessingStatus`
- `getTranscript`
- `getAIReview`

`processMeeting` ต้องเริ่มงานแบบ asynchronous และคืน response ภายในเวลาสั้น โดยไม่รอ provider ถอดเสียงจนเสร็จใน HTTP request เดียว ผลลัพธ์ขั้นต่ำของ `processMeeting`/`getProcessingStatus` ควรมีรูปแบบ provider-neutral ดังนี้:

```json
{
  "meetingId": "meeting_xxx",
  "status": "PROCESSING",
  "steps": {
    "upload": "DONE",
    "transcription": "RUNNING",
    "speakerSeparation": "PENDING"
  },
  "job": {
    "jobId": "job_xxx",
    "state": "RUNNING",
    "attempt": 1,
    "retryable": true
  }
}
```

ห้ามส่ง provider job ID, staging URL, SAS token, raw response หรือ credential ไปยัง frontend/public response `getTranscript` ต้องคืนเฉพาะ normalized segments ตาม Transcript Contract

### Human Review
- `reviewResolution`
- `updateFollowUp`

### Reports
- `generateDraftReport`
- `getReport`
- `updateDraftReport`
- `finalizeReport`
- `generatePdf`
- `publishReport`

### Public
- `publicReport`

## State Rules

Normal lifecycle:

`DRAFT -> RECORDING -> PROCESSING -> REVIEW_REQUIRED -> REPORT_DRAFT -> FINAL -> PUBLISHED`

Backend must reject invalid transitions.

## AI Review Contract

AI Review data must include structured agenda summaries, possible resolutions, follow-up items, responsible parties and due dates only when supported by transcript evidence.

Unknown values must remain null/unspecified.

Resolution states:

- `PENDING`
- `CONFIRMED`
- `REJECTED`

Only `CONFIRMED` resolutions may enter a Final Report.

## Transcript Contract

Each normalized segment contains:

- id
- meetingId
- speaker
- startMs
- endMs
- text
- importantMarker

V1 speaker values use generic labels such as `SPEAKER_1`.

## Processing Status

Processing should expose step states such as:

- upload
- transcription
- speaker separation
- agenda analysis
- resolution detection
- follow-up detection
- draft report generation

Step states:

- `PENDING`
- `RUNNING`
- `DONE`
- `FAILED`

Processing requests should be safe to retry where practical. Repeating `processMeeting` with the same `MeetingID`, audio fingerprint and STT configuration version must reuse an active/successful job where possible rather than create duplicate transcript segments. The backend must persist job state so the user can leave the Processing screen and return later.

For `LIVE` mode, partial transcript events are preview data only. After the meeting ends, the backend must enqueue a `POST` transcription job; only the completed/reviewed post-meeting transcript may feed the AI analysis and Final Report pipeline.

## Transcription Adapter Contract

The backend keeps Speech-to-Text behind a capability-aware adapter. The minimum batch operations are `submitBatch`, `getJobStatus` and `fetchBatchResult`; live operations are optional. Every provider result must normalize to `id`, `meetingId`, `speaker`, `startMs`, `endMs`, `text`, and `importantMarker`. V1 speaker values are generic labels within one meeting and never represent voice identity.

The adapter must classify provider errors into retryable transient failures (for example timeout, rate limit or 5xx) and non-retryable configuration/input failures (for example unsupported locale, invalid audio or authentication). Retry must use the same idempotency key and must not duplicate persisted segments.

## Final Report Contract

Finalization creates a report snapshot. Later edits to draft source data must not silently alter the Final Report.

PDF generation uses Final Report content only.

Publishing creates a public slug and public URL from the Final/PUBLISHED snapshot.

## Audio Delete Guard

Audio deletion is permitted only when all are true:

1. transcription completed
2. AI processing completed
3. Final Report exists
4. user explicitly confirms deletion

After deletion, persist an audit timestamp.

## Public Data Rules

Public report responses may include Final/PUBLISHED report content and PDF download information.

Never expose internal processing errors, secrets, configuration values, temporary audio references or draft content.

## Error Codes

Recommended baseline:

- `VALIDATION_ERROR`
- `NOT_FOUND`
- `INVALID_STATE`
- `TRANSCRIPTION_FAILED`
- `TRANSCRIPTION_AUDIO_TOO_LARGE`
- `TRANSCRIPTION_UNSUPPORTED`
- `AI_OUTPUT_INVALID`
- `AI_PROCESSING_FAILED`
- `PDF_GENERATION_FAILED`
- `AUDIO_DELETE_NOT_ALLOWED`
- `INTERNAL_ERROR`

## Compatibility Rule

Do not silently introduce breaking request/response changes. Update this document whenever API contracts change.
