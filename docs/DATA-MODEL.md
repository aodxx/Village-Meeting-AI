# Data Model — Village Meeting AI

## Principles

- ใช้ UUID/string IDs ไม่ใช้เลขแถวของ Sheet เป็น Primary Key
- ทุก entity ที่แก้ไขได้ควรมี `CreatedAt` / `UpdatedAt`
- เก็บเวลาเป็น ISO 8601 และแสดงผลตาม `Asia/Bangkok`
- Final Report ต้องเป็น snapshot แยกจาก Draft
- Transcript segment ต้องมี start/end timestamp

## Sheet: Meetings

| Column | Type | Required | Description |
|---|---|---:|---|
| MeetingID | string | yes | Primary key |
| Title | string | yes | ชื่อการประชุม |
| MeetingType | string | yes | ประเภทประชุม |
| MeetingDate | date | yes | วันที่ประชุม |
| StartTime | datetime | yes | เวลาเริ่ม |
| EndTime | datetime | no | เวลาจบ |
| Location | string | yes | สถานที่ |
| TranscriptionMode | enum | yes | LIVE / POST |
| Status | enum | yes | State machine |
| PublicSlug | string | no | slug สำหรับ public page |
| AudioFileID | string | no | Drive file id ชั่วคราว |
| AudioDeletedAt | datetime | no | เวลาลบไฟล์เสียง |
| ProcessingError | string | no | error ล่าสุด |
| AudioDurationMs | number | no | ความยาวเสียงที่ตรวจสอบแล้วจากต้นไฟล์ |
| AudioSizeBytes | number | no | ขนาดไฟล์เสียงต้นฉบับที่ตรวจสอบแล้ว |
| AudioMimeType | string | no | MIME type หลังผ่าน preflight |
| AudioFingerprint | string | no | fingerprint สำหรับ idempotency/retry; ไม่ใช่ secret |
| CreatedAt | datetime | yes | created timestamp |
| UpdatedAt | datetime | yes | updated timestamp |

## Sheet: Agendas

| Column | Type | Required | Description |
|---|---|---:|---|
| AgendaID | string | yes | Primary key |
| MeetingID | string | yes | FK -> Meetings |
| AgendaOrder | number | yes | ลำดับ |
| Title | string | yes | ชื่อวาระ |
| Source | enum | yes | USER / AI |
| Summary | long text | no | สรุปโดย AI/ผู้ใช้แก้ |
| Discussion | long text | no | รายละเอียดอภิปราย |
| CreatedAt | datetime | yes | |
| UpdatedAt | datetime | yes | |

## Sheet: TranscriptionJobs

ตารางนี้เป็น operational state สำหรับงาน asynchronous และไม่ใช่ข้อมูลที่เปิดเผยใน Public Report

| Column | Type | Required | Description |
|---|---|---:|---|
| JobID | string | yes | Primary key ของงานภายในระบบ |
| MeetingID | string | yes | FK -> Meetings |
| Mode | enum | yes | LIVE / POST |
| ProviderKey | string | yes | provider key ภายใน; ไม่ส่งออก public |
| ProviderJobRef | string | no | job handle ของ provider; operational metadata |
| IdempotencyKey | string | yes | Meeting + audio fingerprint + config version |
| ConfigVersion | string | yes | version ของ STT configuration |
| Status | enum | yes | PENDING / RUNNING / SUCCEEDED / FAILED / CANCELLED |
| Attempt | number | yes | จำนวน attempt ปัจจุบัน |
| LastPolledAt | datetime | no | เวลาตรวจสถานะล่าสุด |
| NextRetryAt | datetime | no | เวลา retry ถัดไปเมื่อ retry ได้ |
| ErrorCode | string | no | error code ที่จัดประเภทแล้ว |
| ErrorMessage | string | no | readable internal error; ไม่เปิดเผย public |
| SubmittedAt | datetime | no | |
| CompletedAt | datetime | no | |
| CreatedAt | datetime | yes | |
| UpdatedAt | datetime | yes | |

กฎสำคัญคือห้ามมี active job ซ้ำสำหรับ `MeetingID + IdempotencyKey` และการ persist result ต้องตรวจ job/Meeting state ก่อนเขียน `TranscriptSegments`

## Sheet: TranscriptSegments

| Column | Type | Required | Description |
|---|---|---:|---|
| TranscriptID | string | yes | Primary key |
| MeetingID | string | yes | FK |
| Speaker | string | yes | SPEAKER_1, SPEAKER_2... |
| StartMs | number | yes | เวลาเริ่มจากต้นไฟล์ |
| EndMs | number | yes | เวลาจบ |
| Text | long text | yes | ข้อความถอดเสียง |
| ImportantMarker | boolean | yes | อยู่ในช่วงสำคัญหรือไม่ |
| SourceJobID | string | no | FK -> TranscriptionJobs; operational provenance |
| CreatedAt | datetime | yes | |

## Sheet: ImportantMarkers

| Column | Type | Required | Description |
|---|---|---:|---|
| MarkerID | string | yes | Primary key |
| MeetingID | string | yes | FK |
| TimestampMs | number | yes | เวลาที่กดดาว |
| CreatedAt | datetime | yes | |

## Sheet: Resolutions

| Column | Type | Required | Description |
|---|---|---:|---|
| ResolutionID | string | yes | Primary key |
| MeetingID | string | yes | FK |
| AgendaID | string | no | FK -> Agendas |
| ProposedText | long text | yes | ข้อเสนอจาก AI |
| FinalText | long text | no | ข้อความหลังแก้ |
| ReviewStatus | enum | yes | PENDING / CONFIRMED / REJECTED |
| EvidenceStartMs | number | no | ช่วงหลักฐานใน transcript |
| EvidenceEndMs | number | no | ช่วงหลักฐาน |
| CreatedAt | datetime | yes | |
| UpdatedAt | datetime | yes | |

## Sheet: FollowUps

| Column | Type | Required | Description |
|---|---|---:|---|
| FollowUpID | string | yes | Primary key |
| MeetingID | string | yes | FK |
| AgendaID | string | no | FK |
| Title | string | yes | เรื่องที่ต้องทำ |
| Description | long text | no | รายละเอียด |
| ResponsibleParty | string | no | null ถ้าไม่ทราบ |
| DueDate | date | no | null ถ้าไม่ทราบ |
| Source | enum | yes | AI / USER |
| CreatedAt | datetime | yes | |
| UpdatedAt | datetime | yes | |

## Sheet: Reports

| Column | Type | Required | Description |
|---|---|---:|---|
| ReportID | string | yes | Primary key |
| MeetingID | string | yes | FK |
| Version | number | yes | version number |
| Status | enum | yes | DRAFT / FINAL / PUBLISHED |
| ContentJson | long text | yes | normalized report snapshot |
| PdfFileID | string | no | Drive PDF id |
| PublishedAt | datetime | no | |
| CreatedAt | datetime | yes | |
| UpdatedAt | datetime | yes | |

## Sheet: Settings

| Column | Type | Required | Description |
|---|---|---:|---|
| Key | string | yes | setting key |
| Value | string | yes | setting value |
| UpdatedAt | datetime | yes | |

Suggested keys:

- `village.name`
- `village.subdistrict`
- `village.district`
- `village.province`
- `meeting.defaultType`
- `meeting.defaultTranscriptionMode`
- `ai.language`
- `document.paperSize`

## Report JSON Shape

```json
{
  "meeting": {
    "title": "",
    "date": "",
    "time": "",
    "location": "",
    "type": ""
  },
  "agendas": [
    {
      "order": 1,
      "title": "",
      "summary": "",
      "discussion": "",
      "resolutions": []
    }
  ],
  "followUps": []
}
```

## Data Integrity Rules

1. `MeetingID` ต้องมีอยู่ก่อนสร้าง child records
2. `AgendaOrder` ต้องไม่ซ้ำภายใน Meeting เดียวกัน
3. Resolution ที่เข้า Final Report ต้อง `CONFIRMED`
4. Final Report ต้องไม่อ่าน live data จาก Draft หลัง finalize
5. Audio delete ต้องบันทึก `AudioDeletedAt`
6. `TranscriptionJobs` ที่มี `IdempotencyKey` เดียวกันต้องไม่สร้าง transcript segments ซ้ำ
7. Public page ต้องอ้างอิงเฉพาะ Report ที่ `FINAL` หรือ `PUBLISHED`
