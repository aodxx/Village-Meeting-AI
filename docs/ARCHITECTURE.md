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
          |      |--> Local STT Worker (zero STT fee prototype)
          |      +--> External provider adapter (fallback only)
          +--> Gemini Analysis Adapter
```

## 2.1 Official Google Drive Root

Google Drive root ของโปรเจกต์นี้ถูกกำหนดตายตัวเป็น:

- Folder name: `VillageMeetingAI`
- Folder URL: https://drive.google.com/drive/folders/1IEUaLmKAJqgpJaD8jsfdfnda9CmOWODY
- Folder ID: `1IEUaLmKAJqgpJaD8jsfdfnda9CmOWODY`

AI Agent หรือ Backend ที่ได้รับสิทธิ์ Drive ต้องใช้โฟลเดอร์นี้เป็น **root เดียวของโปรเจกต์บน Google Drive** และไม่สร้าง project root ซ้ำในตำแหน่งอื่น เว้นแต่ได้รับคำสั่งโดยตรง

Recommended runtime structure:

```text
VillageMeetingAI/
  01-Meetings/
  02-Audio-Temp/
  03-Transcripts/
  04-Reports/
  05-PDF/
  06-Attachments/
  90-Tests/
  99-Archive/
```

แนวทางการใช้งาน:

- `01-Meetings/` ใช้สำหรับทรัพยากรที่ต้องจัดกลุ่มตามการประชุมเมื่อจำเป็น
- `02-Audio-Temp/` ใช้เก็บเสียงต้นฉบับชั่วคราว และต้องอยู่ภายใต้ Audio Lifecycle ของระบบ
- `03-Transcripts/` ใช้เมื่อมีความจำเป็นต้องเก็บ transcript เป็นไฟล์บน Drive เพิ่มจากข้อมูลในฐานข้อมูล
- `04-Reports/` ใช้สำหรับรายงานที่สร้างโดยระบบ
- `05-PDF/` ใช้สำหรับ Final PDF ที่สร้างจากรายงาน
- `06-Attachments/` ใช้สำหรับเอกสาร/รูปประกอบการประชุมในอนาคต
- `90-Tests/` ใช้เฉพาะไฟล์ทดลอง เดโม และ technical spike
- `99-Archive/` ใช้เก็บไฟล์ที่ไม่ใช้งานประจำแต่ยังต้องการรักษาไว้

ไม่ควรสร้างโฟลเดอร์ย่อยทั้งหมดล่วงหน้าโดยไม่มีความจำเป็น ให้สร้างแบบ on-demand และต้องป้องกัน duplicate folder creation

GitHub เป็น source of truth สำหรับ source code และเอกสารเทคนิคที่ versioned ส่วน Google Drive เป็น workspace สำหรับไฟล์ runtime, เสียง, เอกสารประชุม และไฟล์ที่ระบบสร้าง

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
- Create/persist asynchronous transcription jobs
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
   SpeechToTextAdapter.gs
   TranscriptionJobService.gs
   ReportService.gs
  StorageService.gs
  SheetRepository.gs
  Validation.gs
  Utils.gs
```

> หมายเหตุ: โครงสร้างเป็นแนวทาง ไม่บังคับให้แยกไฟล์ทันทีหากเครื่องมือพัฒนาในช่วงแรกทำงานสะดวกกว่าด้วยไฟล์น้อยกว่า แต่ขอบเขต responsibility ต้องชัดเจน

`StorageService` ต้องอ้างอิง Google Drive root ผ่าน configuration เช่น Script Property ชื่อ `DRIVE_ROOT_FOLDER_ID` โดยค่าของโปรเจกต์นี้คือ `1IEUaLmKAJqgpJaD8jsfdfnda9CmOWODY` ห้าม hard-code ซ้ำกระจัดกระจายในหลายไฟล์

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

### 5.3 Phase 0.1 STT Decision

สำหรับ V1 ภายใต้นโยบาย zero-STT-fee ให้ใช้ **local STT worker** เป็น implementation candidate หลักของ `POST` transcription โดยใช้ Thai-specific model, local speech-boundary detection และ generic speaker-label adapter การตัดสินใจนี้ไม่ทำให้ระบบผูกกับโมเดลหรือ runtime เดียว เพราะผลลัพธ์ต้อง normalize เป็น schema กลางและไม่เปิดเผย implementation ใน frontend, API response หรือ Report layer

Azure Speech Batch Standard ยังคงเป็น paid fallback ที่มีข้อจำกัดเหมาะสมสำหรับกรณี local worker ไม่พร้อม แต่ไม่ใช่ default ภายใต้ policy ใหม่ Azure batch เป็น asynchronous และเอกสารระบุว่า diarization ใช้กับ mono audio, รองรับผู้พูดน้อยกว่า 36 คน และจำกัด source audio 240 นาทีต่อไฟล์เมื่อเปิด diarization ซึ่งครอบคลุมเป้าหมาย V1 1–3 ชั่วโมง [1] [2] หน้าราคา ณ Technical Spike ระบุ `$0.18` ต่อ audio hour และรวม batch diarization แล้ว [3]

**Phase 0.1 zero-STT-fee update:** implementation candidate ที่ผ่าน end-to-end smoke test คือ local worker บน CPU ซึ่งใช้ Thai-specific `biodatlab/distill-whisper-th-small` สำหรับข้อความ, `faster-whisper` base + VAD เป็น speech boundaries และ deterministic acoustic clustering เป็น baseline generic speaker labels [6] [7] วิธีนี้ไม่มีค่า STT ต่อ audio minute แต่ต้องมีเครื่องที่ติดตั้ง Python/model และยังไม่ใช่ production-quality diarization ผล smoke test อยู่ใน `tools/free_stt_spike/` และใช้ synthetic audio ที่ไม่มีข้อมูลส่วนตัว

Azure, Google Cloud, Amazon Transcribe และ OpenAI diarization จึงถูกลดสถานะเป็น paid fallback/benchmark candidates ตาม product policy ใหม่ หากไม่ผ่านข้อกำหนด zero-STT-fee ให้ใช้ local worker ก่อน ระบบต้องเก็บ normalized transcript เดิมและไม่ให้ provider-specific response ไหลไปยัง Report หรือ Public layer

`POST` batch result เป็น authoritative transcript สำหรับ AI analysis และ Final Report ส่วน `LIVE` transcript เป็น preview ระหว่างประชุม เมื่อจบประชุมต้อง enqueue `POST` job ใหม่เพื่อสร้าง transcript ที่ authoritative; live partial result ห้ามใช้ยืนยันมติหรือสร้าง Final Report โดยตรง

### 5.4 Provider-neutral adapter boundary

Adapter ต้องแยกเป็น capability-aware interface โดยมีอย่างน้อย `submitBatch`, `getJobStatus`, `fetchBatchResult` และ optional live methods (`startLive`, `appendLiveAudio`, `stopLive`) provider ที่ไม่รองรับ capability ใดต้องรายงาน `false` ไม่สร้าง fake behavior

ผลลัพธ์จากทุก provider ต้อง normalize เป็น `{ speaker, startMs, endMs, text }` และ map speaker เป็น `SPEAKER_1...` ภายใน Meeting เดียวกันเท่านั้น ห้ามทำ voice identity ข้ามการประชุม การรวม word/phrase timestamp เป็น segment, การบวก chunk offset, การจัดการ overlap และการคำนวณ `ImportantMarker` เป็น responsibility ของ `TranscriptService` ไม่ใช่ Report layer

Raw response, provider job handle และ staging reference เป็น operational metadata ที่ต้องไม่ปรากฏใน Public Report และต้องไม่เก็บ credential/SAS token ไว้ใน Sheet หรือ Drive document

### 5.5 Zero-STT-fee local worker boundary

Apps Script ไม่ควรถูกใช้รัน Python, Whisper model หรือ long-running inference โดยตรง ต้นแบบ Phase 0.1 จึงรันเป็น command-line local worker นอก Apps Script และคืน normalized JSON ตาม adapter contract สำหรับการใช้งาน V1 จริง ต้องเลือกวิธีส่งงานไปยังเครื่องที่ผู้ใช้ควบคุม เช่น worker บนเครื่อง local ที่เปิดใช้งานระหว่าง processing หรือ runtime ที่โครงการมีอยู่แล้ว โดยต้องไม่ถือว่า sandbox ชั่วคราวเป็น production worker

Local worker ต้องรับ audio จาก canonical Drive file หรือไฟล์ที่ผู้ใช้ส่งให้ worker, ทำ preflight, ประมวลผลแบบ bounded chunk, เขียนผลกลับเป็น job result และบันทึก model/config version ทุกครั้ง เมื่อ worker ไม่พร้อมหรือ resource ไม่พอ ระบบต้องคง audio และ job state ไว้เพื่อ retry/fallback ไม่ทำให้ Meeting หรือ Final Report ข้าม state

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

audio เป็น temporary source:

```text
record -> upload -> transcribe -> analyze -> review -> final -> delete on explicit user confirmation
```

Delete guard ต้องตรวจ:

- transcription complete
- AI analysis complete
- final report exists

ไฟล์เสียงจริงต้องถูกวางภายใต้ `VillageMeetingAI/02-Audio-Temp/` หรือโฟลเดอร์ย่อยของ meeting ที่ระบบกำหนด และต้องไม่หลุดออกไปอยู่นอก project root

### 7.1 Provider staging

Provider ที่เลือกใช้ใน Phase 0.1 รับไฟล์จาก object storage ของ provider ไม่ใช่ Google Drive โดยตรง ดังนั้น backend อาจสร้าง staging copy ชั่วคราวไปยัง Azure Blob หรือ object storage ของ fallback provider ได้ แต่ staging copy ต้องผูกกับ `MeetingID`/job, มี TTL, ไม่ใช่ project root และต้องลบหลังดึงผลสำเร็จหรือตาม failure cleanup policy ต้นฉบับใน `VillageMeetingAI/02-Audio-Temp/` เป็น canonical source จนกว่า audio deletion guard จะผ่าน

สำหรับ zero-STT-fee local worker ไม่จำเป็นต้องสร้าง provider staging root ใหม่ ให้ใช้ไฟล์จาก canonical Drive root หรือสำเนาชั่วคราวที่ worker ควบคุม และเก็บผล technical spike ใน `VillageMeetingAI/90-Tests/` เมื่อมีการใช้ Drive runtime artifacts

ห้ามส่งไฟล์เสียงยาวผ่าน Google Sheets หรือรอ provider ให้เสร็จใน Apps Script request เดียว การย้ายไฟล์และการลบ staging ต้องเป็นขั้นตอนที่ retry ได้และตรวจ resource เดิมก่อนสร้างซ้ำ

## 8. Public Report Architecture

Public report endpoint ต้องเป็น read-only

ใช้ `PublicSlug` ที่ไม่เปิดเผย Sheet row index หรือ Drive file ID โดยตรง

Public response ต้องมาจาก Final Report snapshot ไม่ใช่ Draft ที่แก้ไขอยู่

## 9. Security Baseline

- Secrets เก็บใน Apps Script Properties
- ห้าม commit API keys
- ห้ามเก็บ API keys, OAuth tokens หรือ passwords ใน Google Drive
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
- การสร้าง Drive folder/file ต้องป้องกันชื่อหรือ resource ซ้ำจากการ retry

## 11. Performance Considerations

Google Apps Script มี execution limits ดังนั้นงานเสียงยาวต้องออกแบบเผื่อ:

- chunking เมื่อ provider มี file cap
- asynchronous/retry pattern
- external STT provider callbacks/polling หากจำเป็น
- ไม่ส่งไฟล์เสียงขนาดใหญ่ผ่าน Sheet

Apps Script runtime สูงสุด 6 นาทีต่อ execution และ URL Fetch POST/response สูงสุด 50 MB ต่อ call [4] ดังนั้น `processMeeting` ต้องสร้างหรือดำเนินการ job แบบสั้นแล้วจบ ไม่ busy-wait, ไม่โหลดเสียงยาวเข้า Properties และไม่สมมติว่า browser จะเปิดค้างอยู่ การ poll ต้องอ่าน/เขียน operational job state และใช้ backoff เพื่อหลีกเลี่ยง quota exhaustion

Azure batch มี latency แบบ best-effort; เอกสารระบุว่าช่วง peak อาจรอเริ่มงานได้ถึง 30 นาที และ extreme case อาจนานถึง 24 ชั่วโมง [5] UX จึงต้องรองรับ `PROCESSING` ต่อเนื่อง, การออกจากหน้า, refresh และ retry โดยไม่เปลี่ยน Meeting state ผิดลำดับ

Local worker มีข้อจำกัดต่างจาก provider batch: ต้องมี CPU/RAM/disk สำหรับ model cache, ไม่ควรทำงานใน Apps Script execution และความเร็วขึ้นกับ hardware/โมเดล โดยต้นแบบที่ทดสอบใช้ CPU sandbox ประมาณ 44 วินาทีต่อ synthetic audio ประมาณ 38 วินาที การวัดนี้ใช้เป็น smoke-test observation เท่านั้น ไม่ใช่ SLA และไม่ใช่ตัวแทนไฟล์ประชุม 1–3 ชั่วโมง

## 11.1 Idempotent processing contract

ทุก transcription job ต้องมี stable `idempotencyKey` ที่ผูกกับ Meeting, audio fingerprint และ STT configuration version พร้อมเก็บ provider job handle แยกใน operational state การ retry หลัง submit สำเร็จต้องค้นหา job เดิมก่อนสร้างงานใหม่ และการ persist transcript ต้องไม่สร้าง `TranscriptSegments` ซ้ำ

Retry เฉพาะ transient failures เช่น timeout, 429 และ 5xx ด้วย exponential backoff และ jitter ส่วน validation error, unsupported locale, invalid audio และ authentication error ต้องหยุดและส่ง error ที่อ่านได้ให้ผู้ดูแล การที่ผู้ใช้ออกจากหน้า Processing ไม่ถือเป็น cancellation

## Phase 0.1 references

[1]: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-transcription-create "Azure — Create a batch transcription"
[2]: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits "Azure — Quotas and limits for Speech"
[3]: https://azure.microsoft.com/en-us/pricing/details/speech/ "Azure — Speech pricing"
[4]: https://developers.google.com/apps-script/guides/services/quotas "Google Apps Script — Quotas for Google Services"
[5]: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-transcription "Azure — Batch transcription overview"
[6]: https://huggingface.co/biodatlab/distill-whisper-th-small "Biodatlab — distill-whisper-th-small model card"
[7]: https://github.com/SYSTRAN/faster-whisper "SYSTRAN — faster-whisper"

## 12. Future Migration Path

ถ้าระบบโต สามารถย้ายเฉพาะ backend processing ไป Cloud Run / Functions / Supabase โดยคง:

- frontend contracts
- normalized transcript schema
- meeting/report data model
- AI adapters

ดังนั้น API Contract และ IDs ต้องไม่ผูกกับ Sheet row number
