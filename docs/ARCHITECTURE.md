# Technical Architecture — Village Meeting AI

## 1. Architecture Goals

V1 ต้องเน้นต้นทุนต่ำ ดูแลง่าย เหมาะกับงานหมู่บ้าน และไม่ผูก Speech-to-Text หรือ AI provider จนเปลี่ยนไม่ได้

## 2. High-Level Architecture

```text
Mobile / Desktop Browser
        |
        v
   PWA Frontend
        |
        v
Google Apps Script Web App API
   |        |         |
   |        |         +--> Google Drive
   |        |              - Temporary audio
   |        |              - Generated PDF
   |        |
   |        +--> Google Sheets
   |               - Meetings
   |               - Agendas
   |               - Transcript
   |               - Resolutions
   |               - FollowUps
   |               - Reports
   |
   +--> AI Service Layer
          |--> Speech-to-Text Adapter
          +--> Gemini Analysis Adapter
```

## 3. Frontend

Mobile-first PWA responsibilities:

- Meeting form and agenda management
- Microphone permission and recording UX
- Pause/Resume
- Important Marker
- Upload audio chunks/file
- Processing status
- Transcript review
- AI review
- Report editor
- Publish/share/download flow
- Meeting history and settings

Frontend ห้ามฝัง API Key หรือ secrets

## 4. Backend — Google Apps Script

Apps Script เป็น API orchestration layer:

- Validate requests
- Generate IDs
- Read/write Google Sheets
- Manage Google Drive files
- Call AI adapters
- Enforce meeting state transitions
- Generate report payload/PDF
- Public report read endpoint

ควรแยก logical modules แม้ Apps Script จะถูก deploy เป็น Web App เดียว

Suggested modules:

```text
appsscript/
  Code.gs
  Router.gs
  Config.gs
  MeetingService.gs
  AgendaService.gs
  TranscriptService.gs
  AIService.gs
  ReportService.gs
  StorageService.gs
  SheetRepository.gs
  Validation.gs
  Utils.gs
```

> หมายเหตุ: โครงสร้างเป็นแนวทาง ไม่บังคับให้แยกไฟล์ทันทีหากเครื่องมือพัฒนาในช่วงแรกทำงานสะดวกกว่าด้วยไฟล์น้อยกว่า แต่ขอบเขต responsibility ต้องชัดเจน

## 5. AI Service Layer

แยกเป็น 2 งาน

### 5.1 Speech-to-Text Adapter

Interface ต้องคืน transcript segments แบบมาตรฐาน เช่น:

```json
{
  "segments": [
    {
      "speaker": "SPEAKER_1",
      "startMs": 1000,
      "endMs": 8200,
      "text": "..."
    }
  ]
}
```

Provider สามารถเปลี่ยนได้ในอนาคตโดยไม่กระทบ Report layer

### 5.2 Gemini Analysis Adapter

รับ normalized transcript + agenda + important markers

คืน Structured JSON เท่านั้นสำหรับ:

- agenda mapping
- summaries
- discussion points
- possible resolutions
- follow-ups
- responsible party
- due date

ต้อง validate schema ก่อนบันทึกลง Sheets

## 6. State Machine

```text
DRAFT
  -> RECORDING
  -> PROCESSING
  -> REVIEW_REQUIRED
  -> REPORT_DRAFT
  -> FINAL
  -> PUBLISHED
```

Allowed exceptions:

- RECORDING -> DRAFT หากยกเลิกโดยไม่เก็บข้อมูล
- PUBLISHED ยังคง Final snapshot เดิมสำหรับ public view

Backend ต้องปฏิเสธ state transition ที่ไม่ถูกต้อง

## 7. Audio Lifecycle

Audio เป็น temporary source:

```text
record -> upload -> transcribe -> analyze -> review -> final -> delete on explicit user confirmation
```

Delete guard ต้องตรวจ:

- transcription complete
- AI analysis complete
- final report exists

## 8. Public Report Architecture

Public report endpoint ต้องเป็น read-only

ใช้ `PublicSlug` ที่ไม่เปิดเผย Sheet row index หรือ Drive file ID โดยตรง

Public response ต้องมาจาก Final Report snapshot ไม่ใช่ Draft ที่แก้ไขอยู่

## 9. Security Baseline

- Secrets เก็บใน Apps Script Properties
- ห้าม commit API keys
- Validate content type/size ของ upload
- Sanitize text ก่อน render public page
- Public route read-only
- Admin/write actions ต้องไม่แชร์ endpoint semantics กับ public mutation
- Log errors โดยไม่ log secret/token/audio content แบบไม่จำเป็น

## 10. Reliability

ทุก processing step ควร idempotent เท่าที่ทำได้

ตัวอย่าง:

- การเรียก `processMeeting` ซ้ำไม่ควรสร้าง report ซ้ำหลายชุดโดยไม่มี version
- Upload completion ควรตรวจ MeetingID และ state
- AI output invalid ต้องเก็บ error state/message และให้ retry ได้

## 11. Performance Considerations

Google Apps Script มี execution limits ดังนั้นงานเสียงยาวต้องออกแบบเผื่อ:

- chunking
- asynchronous/retry pattern
- external STT provider callbacks/polling หากจำเป็น
- ไม่ส่งไฟล์เสียงขนาดใหญ่ผ่าน Sheet

ก่อน implementation จริงต้องทำ Technical Spike เรื่องการประชุม 1–3 ชั่วโมงเพื่อยืนยันว่า Apps Script orchestration เพียงพอ

## 12. Future Migration Path

ถ้าระบบโต สามารถย้ายเฉพาะ backend processing ไป Cloud Run / Functions / Supabase โดยคง:

- frontend contracts
- normalized transcript schema
- meeting/report data model
- AI adapters

ดังนั้น API Contract และ IDs ต้องไม่ผูกกับ Sheet row number
