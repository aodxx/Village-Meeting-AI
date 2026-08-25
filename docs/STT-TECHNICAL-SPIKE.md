# STT Technical Spike — Thai Village Meetings

**Phase:** 0.1 Technical Spike

**วันที่:** 2026-08-26

**สถานะ:** Recommendation ready; empirical audio benchmark pending representative meeting recordings

**ผู้จัดทำ:** Manus AI

## 1. Executive Summary

Technical Spike นี้ประเมินแนวทาง Speech-to-Text สำหรับการประชุมหมู่บ้านภาษาไทยที่มีหลายผู้พูดและมีความยาวเป้าหมาย 1–3 ชั่วโมง โดยยึดข้อกำหนด V1 ว่า Transcript ต้องมี timestamp และ generic speaker labels เช่น `SPEAKER_1`, AI ห้ามเดาข้อมูลจากเสียง และมติที่เข้า Final Report ต้องผ่านการยืนยันโดยมนุษย์เท่านั้น

ข้อเสนอสำหรับ V1 คือใช้ **Azure AI Speech Batch Transcription — Standard** เป็น provider หลักของเส้นทาง **POST transcription** โดยใช้ locale `th-TH`, audio แบบ mono, batch REST API v3.2 หรือใหม่กว่า, เปิด diarization และรับผลแบบ asynchronous การเลือกนี้ไม่ได้ทำให้ระบบผูกติดกับ Azure เพราะระบบจะเก็บเพียง normalized transcript และสถานะงานแบบ provider-neutral ส่วน audio ต้นฉบับยังอยู่ภายใต้ Google Drive root `VillageMeetingAI/02-Audio-Temp/` ตาม lifecycle เดิม และ Azure Blob ที่ใช้เป็น staging ต้องเป็นพื้นที่ชั่วคราวของ provider ไม่ใช่ project root ใหม่

เหตุผลสำคัญคือ Azure ระบุการรองรับ batch Thai, diarization สำหรับ mono audio, word-level timestamps และเพดานไฟล์ 1 GB/240 นาทีเมื่อเปิด diarization โดยราคาหน้า official ที่ตรวจสอบระบุ Standard Batch ที่ `$0.18` ต่อ audio hour และรวม diarization ใน batch แล้ว [1] [2] [3] [4] อย่างไรก็ตาม การรองรับเชิงเอกสารไม่ใช่หลักฐานว่าเสียงประชุมหมู่บ้านที่มีเสียงรบกวนและการพูดทับกันจะมีคุณภาพเพียงพอ จึงต้องทำ benchmark กับไฟล์เสียงจริงหรือไฟล์ทดสอบที่ผู้ใช้อนุมัติก่อนเปิดใช้งาน production

สำหรับ **LIVE transcription** ยังคงอยู่ใน Scope V1 แต่ควรถือเป็น provisional/preview text เท่านั้น ส่วน Transcript ที่เป็นแหล่งอ้างอิงสำหรับ AI analysis และ Final Report ควรประมวลผลซ้ำด้วย batch หลังจบประชุม เพื่อให้ได้ผลลัพธ์ที่สม่ำเสมอและลดความเสี่ยงจาก session หลุดหรือ speaker label ที่เปลี่ยนระหว่างช่วงเสียง

## 2. Scope และข้อจำกัดที่ใช้ตัดสิน

| ประเด็น | ข้อกำหนดของ V1 | ผลต่อการเลือก STT |
|---|---|---|
| ภาษา | ภาษาไทยเป็นภาษาหลัก ใช้ locale ที่ชัดเจน | ต้องมี Thai support แบบเป็นทางการและต้องทดสอบศัพท์ชุมชน/ชื่อเฉพาะ |
| ผู้พูด | หลายผู้พูด แต่ V1 ใช้เพียง `SPEAKER_1`, `SPEAKER_2`, ... ไม่ทำ voice identity | ต้องมี diarization หรือมีวิธีประกอบ diarizer ที่เชื่อถือได้ |
| ความยาว | เป้าหมาย 1–3 ชั่วโมง | ต้องเป็น asynchronous long-form ไม่รอใน HTTP request เดียว |
| ผลลัพธ์ | segment มี speaker, start/end timestamp, text | provider response ต้อง normalize เป็น schema เดียว |
| โหมด | LIVE และ POST | LIVE ใช้เพื่อแสดงข้อความระหว่างประชุม; POST เป็น authoritative transcript |
| Storage | Google Drive root เดิมเป็น project root เดียว | ห้ามสร้าง project root ใหม่; provider staging ต้องชั่วคราวและลบได้ |
| Backend | Google Apps Script Web App เป็น orchestration layer | จำกัด execution 6 นาที, ต้องใช้ job state, polling/retry และไม่ส่งไฟล์เสียงผ่าน Sheets |
| ความถูกต้องของรายงาน | Final Report เป็น snapshot และ public report อ่านจาก Final Report เท่านั้น | ห้ามผูก report layer กับ provider response หรือ draft data แบบสด |
| ความปลอดภัย | ห้าม commit API key/OAuth token/ข้อมูลประชุมส่วนตัว | credentials อยู่ใน secret store/Apps Script Properties; log ต้องไม่บันทึกเสียงหรือ token โดยไม่จำเป็น |

## 3. ข้อจำกัดของสถาปัตยกรรมปัจจุบัน

ปัจจุบัน Repository มีเอกสารสถาปัตยกรรมและโครงสร้าง Apps Script placeholder แต่ยังไม่มี implementation, audio fixture หรือ benchmark harness ใน Repository ดังนั้นการตรวจสอบรอบนี้เป็น **architecture and provider feasibility spike** ไม่ใช่ผลวัด WER ของเสียงประชุมจริง ข้อค้นพบนี้เป็นข้อจำกัดสำคัญ: ยังไม่ควรประกาศว่า provider ใดมีความแม่นยำเพียงพอสำหรับเสียงหมู่บ้านจนกว่าจะมีชุดทดสอบภาษาไทยที่ผู้ใช้อนุมัติ

Google Apps Script มี runtime สูงสุด 6 นาทีต่อ execution ทั้ง consumer และ Workspace account, URL Fetch POST/response สูงสุด 50 MB ต่อ call, simultaneous executions 30 ต่อ user และ trigger 20 ต่อ user ต่อ script [5] ข้อจำกัดเหล่านี้ทำให้การอัปโหลดหรือรอ batch job ใน `processMeeting` request เดียวไม่ปลอดภัย แม้ไฟล์เสียงจะสามารถมีขนาดเล็กพอที่จะผ่าน 50 MB ได้ก็ตาม

แนวทางที่รองรับคือให้ Apps Script สร้าง job record และคืนสถานะเร็ว จากนั้น worker แบบ execution สั้น ๆ หรือการเรียก status endpoint จะ submit/poll/fetch ตาม state ที่บันทึกไว้ เมื่อ provider ทำงานเสร็จจึง normalize transcript และเขียน `TranscriptSegments` แบบ idempotent การออกจากหน้า Processing จึงไม่ทำให้ pipeline หยุด และการ retry จะไม่สร้าง segment ซ้ำ

Google Drive ยังคงเป็น canonical workspace ของระบบตามที่ระบุใน `AGENTS.md` และ `docs/ARCHITECTURE.md` ไฟล์เสียงต้นฉบับต้องอยู่ใต้ `VillageMeetingAI/02-Audio-Temp/` ส่วนการส่งไป Azure Blob, Amazon S3 หรือ Google Cloud Storage ให้ถือเป็น **provider staging copy** ที่มี TTL และลบหลังได้ผลหรือเมื่อ job หมดอายุ ไม่สร้างโฟลเดอร์ project root แยกใน cloud provider ใด

## 4. Provider comparison

ตัวเลขราคาเป็นข้อมูลจากหน้า official ที่ตรวจสอบเมื่อ 2026-08-26 และอาจเปลี่ยนตาม region, tier, API version หรือโปรโมชั่น จึงต้อง re-check ในขั้น implementation ก่อนกำหนด budget จริง

| แนวทาง | Thai support | Long audio | Speaker diarization | Input/output และ orchestration | ต้นทุนที่ตรวจสอบได้ | ความเสี่ยงต่อ V1 |
|---|---|---|---|---|---|---|
| **Azure Speech Batch Standard** | รองรับ `th-TH` ในตาราง Speech-to-text | Standard batch จำกัดไฟล์ 1 GB; เมื่อเปิด diarization จำกัด 240 นาที/ไฟล์ ซึ่งครอบคลุมเป้าหมาย 1–3 ชั่วโมง | Mono audio; สูงสุดน้อยกว่า 36 speakers; 2 speakers ใช้ `diarizationEnabled`, 3+ speakers ใช้ diarization config | Asynchronous; ต้องใช้ Azure Blob `contentUrls`/`contentContainerUrl`; คืนผลผ่าน files endpoint; รองรับ word timestamps | `$0.18/audio hour` สำหรับ Standard Batch; batch diarization รวมในราคา; 1–3 ชั่วโมงประมาณ `$0.18–$0.54` ต่อ meeting ก่อน staging/storage [1] [2] [3] | ต้องเพิ่ม transient Azure Blob staging และควบคุม TTL; latency best-effort อาจรอเริ่ม 30 นาที และ extreme case อาจถึง 24 ชั่วโมง [4] |
| **Google Cloud Speech-to-Text V2** | `th-TH` มี `chirp`, `chirp_2` และ `chirp_3/long` ตาม region/model table | Batch รับ Cloud Storage URI, สูงสุด 5 files/request, แต่ละไฟล์สูงสุด 8 ชั่วโมง | Guide มี diarization แต่ current Thai rows ใน feature table ไม่แสดง diarization flag อย่างชัดเจน จึงยังไม่ควรสัญญา Thai diarization | Asynchronous Operation; ต้องใช้ GCS staging; synchronous จำกัด 10 MB/1 นาที, streaming จำกัด 5 นาที/stream | V2 Standard `$0.016/minute`; 1–3 ชั่วโมงประมาณ `$0.96–$2.88` ต่อ meetingก่อน GCS [6] [7] [8] [9] | Long audio ดี แต่ข้อสงสัยเรื่อง Thai diarization เป็น blocker หลัก; ต้องทำ compatibility probe ก่อนใช้เป็น primary |
| **Amazon Transcribe Standard Batch** | `th-TH` รองรับ batch และ streaming ตาม language table | สูงสุด 28,800 วินาที (8 ชั่วโมง) และ 2 GB ต่อไฟล์ | สูงสุด 30 speakers (`spk_0`–`spk_29`), ต้องตั้ง `ShowSpeakerLabels` และ `MaxSpeakerLabels` | รับ S3 URI; JSON มี word/audio segment timestamps และ `speaker_labels`; รองรับ queue สูงสุด 10,000 jobs | คิดตามวินาทีแบบ tiered/region; official high-volume example ใช้ `$0.006/minute` ที่ 2M นาที/เดือน แต่ไม่ควรนำไปใช้เป็น low-volume rate; มี free tier 60 นาที/เดือน 12 เดือน [10] [11] [12] [13] | Technical fit ดี แต่ต้องมี S3 staging, IAM และตรวจราคา/region; language table ไม่ได้ให้หลักฐานคุณภาพ Thai meeting โดยตรง |
| **OpenAI `gpt-4o-transcribe-diarize`** | API รับ language hints ของ `gpt-transcribe`; Whisper รองรับหลายภาษาแต่ accuracy varies by language | Transcription API จำกัด 25 MB/ไฟล์ ต้องบีบอัดหรือแบ่ง chunk; เสียง 1–3 ชั่วโมงจึงต้อง chunking | Built-in diarization; `diarized_json` มี speaker/start/end; ไฟล์เกิน 30 วินาทีต้อง `chunking_strategy=auto` หรือ VAD | เหมาะกับ synchronous/chunked API; speaker labeling ไม่รองรับ Realtime sessions; diarize model ไม่รองรับ prompts | Model page แสดง `$2.50/1M input audio tokens` และ `$10/1M output tokens`; ไม่ใช่ per-minute rate จึงต้องวัดจาก usage จริง [14] [15] | คุณภาพ/diarization น่าสนใจ แต่ 25 MB, chunk dedupe, token cost และไม่มี prompt สำหรับศัพท์เฉพาะทำให้ไม่เหมาะเป็น default path ตอนนี้ |
| **Self-hosted Whisper + pyannote** | Whisper เป็น multilingual ASR; รองรับ Thai แต่ความแม่นยำต้อง benchmark เอง | ไม่มี API file cap โดยตรง แต่ต้องจัดการ sliding 30-second windows, disk, CPU/GPU และ queue เอง | pyannote แยกผู้พูดได้และรับ `num_speakers`/range; ต้องรัน pipeline แยก | ต้องมี worker/container/runtime นอก Apps Script; offline ได้หลังดาวน์โหลด model | ค่า API ต่ำ/ไม่มี แต่มีค่า compute, storage, operations และ model access/license; ไม่มีตัวเลขต่อ meeting ที่รับประกัน | ควบคุมข้อมูลและ provider lock-in ดี แต่ซับซ้อนเกิน default V1 และเพิ่มภาระดูแลระบบ [16] [17] |

## 5. ข้อเสนอแนะสำหรับ V1

### 5.1 Primary path: Azure Batch Standard สำหรับ POST

ให้เลือก Azure Speech Batch Standard เป็น default adapter ของ `TranscriptionMode=POST` ด้วย configuration ต่อไปนี้:

| Configuration | V1 recommendation |
|---|---|
| Locale | `th-TH` |
| Audio preprocessing | Convert/validate เป็น mono; แนะนำ WAV PCM 16-bit หรือ FLAC ตามผล benchmark; ไม่ควร downmix แบบเงียบโดยไม่บันทึก metadata |
| Batch API | Speech-to-text REST API v3.2 หรือใหม่กว่า |
| Diarization | เปิดใช้งาน; ค่า speaker range เป็น configuration ไม่ใช่ชื่อบุคคล; default ให้ทดลองกับ 2–12 และปรับตามข้อมูลจริง โดยต้องไม่เกิน provider limit |
| Timestamps | เปิด word-level timestamps แล้ว aggregate เป็น normalized segments; เก็บ start/end เป็น milliseconds จากต้นฉบับ |
| Storage | ต้นฉบับใน Drive root; copy ชั่วคราวไป Azure Blob ด้วย TTL; ผล provider ดึงกลับและลบ staging เมื่อปลอดภัย |
| Authority | POST batch result เป็น source สำหรับ AI analysis; LIVE result เป็น preview และต้อง reconcile ด้วย POST หลังจบประชุม |
| Retry | บันทึก provider job handle และ attempt state; retry เฉพาะ transient error/timeout/429/5xx; validation/auth/file errors ต้องหยุดและให้มนุษย์แก้ |

เหตุผลที่ไม่เลือก Google Cloud เป็น primary แม้ระบบใช้ Google Drive/Sheets คือ current V2 language table แสดง Thai models แต่ไม่ได้ยืนยัน diarization สำหรับ Thai ใน feature column อย่างชัดเจน การใช้ Google ต้องผ่าน compatibility probe ที่ตรวจ `th-TH` + batch + diarization + timestamp ก่อนจึงพิจารณาเป็น provider สำรองหรือสลับ primary

AWS Transcribe เป็น fallback ที่มี technical fit ใกล้เคียง โดยเฉพาะเพดาน 8 ชั่วโมง/2 GB และ 30 speakers แต่มี S3/IAM staging เพิ่มอีกแบบ ส่วน OpenAI diarize ควรใช้เป็น benchmark/fallback สำหรับ chunked audio มากกว่าจะเป็น default เพราะ file cap 25 MB และต้นทุน audio-token ที่ต้องวัดจริง

### 5.2 LIVE path ภายใน Scope เดิม

V1 ไม่ควรลบตัวเลือก LIVE transcription ออก แต่ควรกำหนด contract ให้ชัดว่า live text ใช้เพื่อช่วยผู้บันทึกระหว่างประชุมและอาจหาย/แก้ไขได้ ระบบต้องเก็บ audio ต้นฉบับต่อไป และเมื่อกดจบประชุมต้อง enqueue POST batch job เพื่อสร้าง authoritative transcript ใหม่ การแสดง speaker ใน live mode อาจเป็น provisional generic label และไม่ควรให้ AI สร้างมติหรือ Final Report จาก live partial state ก่อน batch/review สำเร็จ

การออกแบบนี้รักษา UX เดิมใน PRD/UX Flow โดยไม่อ้างว่า live session เป็นหลักฐานสุดท้าย และลดผลกระทบจาก mobile network, session timeout และ speaker assignment ที่ยังไม่ final ระหว่าง stream

## 6. Provider-neutral Speech-to-Text Adapter

### 6.1 Separation of responsibilities

Adapter มีหน้าที่คุยกับ provider, จัดการ provider job, แปลงผลลัพธ์เป็น schema กลาง และส่งต่อ error ที่จัดประเภทแล้วเท่านั้น Adapter ไม่ควรตัดสินว่าวาระใดสำคัญ ไม่ควรสร้างมติ ไม่ควรระบุชื่อบุคคลจากเสียง และไม่ควรเขียน Final Report โดยตรง

`TranscriptService` เป็นผู้ตรวจ schema, map marker, deduplicate retry result และเขียน `TranscriptSegments` ส่วน `AIService` รับ normalized transcript เท่านั้น การแยกชั้นนี้ทำให้เปลี่ยน Azure เป็น AWS/Google/OpenAI ได้โดยไม่เปลี่ยน Report layer

### 6.2 Proposed interface

ตัวอย่างสัญญาภายในที่ provider-neutral:

```ts
interface SpeechToTextAdapter {
  providerId(): string;
  capabilities(): {
    batch: boolean;
    live: boolean;
    diarization: boolean;
    wordTimestamps: boolean;
    maxAudioMinutes?: number;
    maxFileBytes?: number;
  };

  submitBatch(request: BatchTranscriptionRequest): ProviderJobHandle;
  getJobStatus(handle: ProviderJobHandle): ProviderJobStatus;
  fetchBatchResult(handle: ProviderJobHandle): ProviderTranscript;
  cancel?(handle: ProviderJobHandle): void;

  // Optional live capability. A provider that cannot support live must
  // report live=false rather than forcing a fake implementation.
  startLive?(request: LiveTranscriptionRequest): LiveSessionHandle;
  appendLiveAudio?(handle: LiveSessionHandle, audioChunk: ArrayBuffer): LiveEvents;
  stopLive?(handle: LiveSessionHandle): void;
}
```

สำหรับ Apps Script ที่ไม่ได้ใช้ TypeScript จริง ให้รักษา shape เดียวกันด้วย plain objects และ validation functions โดยไม่ให้ชื่อ field ของ Azure/AWS/Google หลุดออกไปยัง API response ของระบบ

```json
{
  "meetingId": "meeting_xxx",
  "mode": "POST",
  "languageCode": "th-TH",
  "audio": {
    "driveFileId": "drive_file_xxx",
    "sha256": "optional-audio-fingerprint",
    "durationMs": 7200000,
    "mimeType": "audio/wav",
    "sizeBytes": 123456789
  },
  "diarization": {
    "enabled": true,
    "minSpeakers": 2,
    "maxSpeakers": 12
  },
  "idempotencyKey": "meeting_xxx:audio_sha256:stt_config_v1"
}
```

Provider result ต้องถูกแปลงเป็น:

```json
{
  "segments": [
    {
      "speaker": "SPEAKER_1",
      "startMs": 1000,
      "endMs": 8200,
      "text": "..."
    }
  ],
  "metadata": {
    "languageCode": "th-TH",
    "providerId": "opaque-internal-value",
    "sourceDurationMs": 7200000
  }
}
```

`providerId`, provider job ID, URI, SAS token และ raw response เป็น operational metadata ไม่ใช่ public report data และต้องไม่ถูกส่งไปยัง Public Report endpoint

### 6.3 Normalization rules

1. ตรวจว่าทุก segment มี `speaker`, `startMs`, `endMs`, `text`; timestamp ต้องเป็นจำนวนเต็มไม่ติดลบ และ `endMs > startMs` เมื่อมีข้อความ
2. แปลง provider labels เช่น `spk_0`, `Speaker 1` หรือ numeric label เป็น `SPEAKER_1...` ที่ stable ภายใน Meeting เดียวกันเท่านั้น ห้ามตีความเป็นชื่อจริงหรือ identity ข้ามการประชุม
3. ใช้ phrase/word timestamps ของ provider และ aggregate ตาม speaker turn/utterance โดยห้ามเปลี่ยนข้อความให้มี facts เพิ่ม
4. สำหรับ chunked fallback ให้บวก `chunkOffsetMs`, จัดการ overlap และ deduplicate เฉพาะข้อความที่ซ้ำจากขอบ chunk; หาก dedupe ไม่มั่นใจให้เก็บ segment ไว้เพื่อ human review แทนการลบหลักฐาน
5. ตรวจลำดับเวลาและเสียงพูดทับกัน; ห้ามบังคับให้ segment ที่ overlap ถูกจัดเป็นผู้พูดเดียวโดยไม่มีหลักฐาน
6. `ImportantMarker` ไม่ใช่ข้อมูลจาก provider ให้คำนวณภายหลังจาก `ImportantMarkers.TimestampMs` ด้วย interval overlap และทำซ้ำได้อย่าง idempotent
7. เก็บ raw provider result เป็นไฟล์ชั่วคราวภายใต้ Drive `90-Tests/` เฉพาะ technical spike หรือภายใต้ meeting runtime ที่เหมาะสมเมื่อ implementation จริง; ห้ามใส่ raw response ขนาดใหญ่ใน Sheets หากไม่จำเป็น

## 7. Asynchronous orchestration และ retry

ลำดับการทำงานที่เสนอคือ `register audio → validate metadata → create provider staging copy → submit provider job → persist job handle → poll → fetch result → validate/normalize → persist segments → mark transcription DONE → continue AI pipeline` ทุกขั้นต้องตรวจ `MeetingID` และ state ก่อนเขียนข้อมูล

| สถานการณ์ | การดำเนินการ |
|---|---|
| submit สำเร็จ | บันทึก job handle, provider, config version, submitted time และเปลี่ยน transcription step เป็น `RUNNING` |
| poll ยังไม่เสร็จ | บันทึก `lastPolledAt`/status แล้วจบ execution; ไม่ busy-wait ใน Apps Script |
| provider 429/5xx/timeout | retry ด้วย exponential backoff และ jitter โดยใช้ idempotency key เดิม |
| provider validation/auth/unsupported locale | หยุด retry อัตโนมัติ, เก็บ readable error, เปลี่ยน step เป็น `FAILED` และให้ผู้ดูแลแก้ configuration |
| result ได้แต่ schema ไม่ผ่าน | ห้ามเขียนบางส่วนลง Sheets; เก็บ error `TRANSCRIPTION_FAILED`/รายละเอียดภายใน และเปิด retry หรือ manual inspection |
| retry หลัง result สำเร็จ | ตรวจ fingerprint/job state และไม่สร้าง TranscriptSegments ซ้ำ |
| user ออกจาก Processing | ไม่ยกเลิก job; หน้ากลับมาอ่าน `getProcessingStatus` จาก persisted state |
| provider staging หมดอายุ | ไม่ลบ canonical Drive audio; mark job failed และให้ retry จากต้นฉบับเมื่อยังอยู่ใน lifecycle |

เวลาการ poll ไม่ควรใช้คงที่แบบถี่มาก เริ่มด้วย backoff ระดับนาทีสำหรับ batch และมีเพดานตาม provider TTL/UX policy เพราะ Azure ระบุว่า batch เป็น best-effort, อาจรอเริ่มถึง 30 นาที และ 90th percentile normalized latency น้อยกว่า 6 ชั่วโมง แต่ extreme case อาจนานถึง 24 ชั่วโมง [4]

## 8. File, time และ cost envelope

| รายการ | ข้อสรุปสำหรับ V1 |
|---|---|
| เป้าหมายเวลา | 1–3 ชั่วโมงอยู่ใน Azure diarization limit 240 นาที/ไฟล์; 3 ชั่วโมงมี margin 60 นาที |
| Azure file size | สูงสุด 1 GB ต่อไฟล์ใน Standard batch; ต้องตรวจขนาดก่อน staging |
| รูปแบบไฟล์แนะนำ | WAV PCM 16-bit mono หรือ FLAC หลังทดสอบคุณภาพ; เก็บ original metadata และอย่า overwrite ต้นฉบับโดยอัตโนมัติ |
| Apps Script upload | URL Fetch POST/response 50 MB/call จึงไม่ควรส่ง audio ผ่าน Apps Script; ใช้ Drive/Blob resumable หรือ provider-side staging flow |
| Azure batch latency | ไม่รับประกันทันที; UX ต้องรองรับ `PROCESSING` ต่อเนื่องและ retry/refresh |
| Azure STT-only cost | ประมาณ `$0.18–$0.54` ต่อ 1–3 ชั่วโมง; ยังไม่รวม Azure Blob, network, Apps Script, และการเรียก AI analysis |
| Google STT-only reference | ประมาณ `$0.96–$2.88` ที่ `$0.016/minute`; ยังไม่รวม GCS และต้องยืนยัน Thai diarization |
| AWS cost | ใช้ tier/region calculator; อย่าใช้ high-volume `$0.006/minute` เป็นราคาของโครงการขนาดเล็กโดยอัตโนมัติ |
| OpenAI cost | ใช้ audio-token usage จาก dashboard/probe; 25 MB limit ทำให้ต้องรวมค่า chunking, upload และ dedupe ใน latency/cost budget |
| File-size illustration | 16 kHz mono WAV 16-bit มีข้อมูลประมาณ 115.2 MB ต่อชั่วโมง หรือ 345.6 MB ต่อ 3 ชั่วโมงก่อน container overhead; จึงอยู่ใต้ Azure 1 GB แต่ไม่เหมาะกับ OpenAI 25 MB |

ค่าใช้จ่ายข้างต้นเป็น **STT-only estimate** ไม่ใช่ค่าใช้จ่ายทั้งระบบ การตัดสินใจ production ต้องบันทึก `audioDurationSeconds`, provider usage และ processing outcome ต่อ job เพื่อเทียบ estimated กับ actual cost และตรวจ anomaly

## 9. Benchmark ที่ต้องทำก่อน Production

Repository ยังไม่มี audio fixture จึงยังไม่ถือว่า long-meeting spike ผ่านในเชิงคุณภาพ ชุดทดสอบที่ต้องจัดเตรียมควรเป็นเสียงภาษาไทยที่ผู้ใช้มีสิทธิ์ให้ทดสอบและลบได้ โดยแบ่งอย่างน้อยเป็นคลิปสั้นสำหรับ smoke test และคลิปยาว/หลายผู้พูดสำหรับ end-to-end test การใช้เสียงสังเคราะห์แทนเสียงประชุมจริงอาจช่วยตรวจ API contract ได้ แต่ไม่ควรใช้ตัดสิน WER หรือ diarization quality

| Test case | สิ่งที่ต้องวัด | Gate เบื้องต้นที่ควรกำหนดร่วมกับผู้ใช้ |
|---|---|---|
| Thai clear speech, 2 speakers | transcript readability, timestamp validity, speaker switch | ไม่มี job failure; segments อ่านได้และไม่สลับ speaker อย่างเป็นระบบ |
| 4–8 speakers, one microphone | diarization purity/coverage, speaker count stability | generic labels ครบ; สัดส่วนสลับ speakerผิดต้อง review ได้ |
| Background noise/echo | omission, hallucinated words, punctuation | ห้ามมีข้อความที่ไม่มีเสียงจริงในช่วงที่ตรวจ; จุดไม่แน่ใจต้องส่ง human review |
| Overlapping speech | overlap handling and timestamp behavior | ไม่ merge เป็น speaker เดียวโดยอัตโนมัติ; เก็บ timestamps ให้ตรวจสอบได้ |
| 1-hour and 3-hour audio | submit-to-complete latency, size, memory, retry | ไม่พึ่ง browser ค้าง; job กลับมาทำต่อได้หลัง refresh |
| provider failure/429/timeout | idempotency and retry | retry ไม่สร้าง duplicate segments และ error อ่านรู้เรื่อง |
| marker alignment | marker-to-segment overlap | marker เดิมแสดงกับ segment ที่เกี่ยวข้องหลัง re-run |
| finalization safety | report snapshot/public isolation | transcript/AI retry ไม่เปลี่ยน Final Report ที่ finalize แล้ว |

ผล benchmark ต้องบันทึก provider/model/API version, region, audio metadata, job timestamps, cost usage, failure/retry count และ sample output ที่ redacted แล้วใน `VillageMeetingAI/90-Tests/` เท่านั้นเมื่อผู้ใช้อนุมัติการใช้ Drive runtime test artifacts

## 10. Decision และงานถัดไป

**Decision:** ทำ Azure Speech Batch Standard เป็น implementation candidate หลักสำหรับ Phase 3 Transcription โดยยังคง `SpeechToTextAdapter` เป็น provider-neutral และไม่เปิดเผย provider job details ใน API/Public Report ผล batch จะเป็น authoritative transcript ส่วน live จะเป็น preview ที่ต้อง re-run หลังจบประชุม

**Open condition:** ก่อน production ต้องจัดทำ compatibility/quality benchmark กับเสียงภาษาไทยหลายผู้พูดและเสียงรบกวนจริงที่ได้รับอนุญาต หาก Azure Thai diarization หรือคุณภาพไม่ผ่านเกณฑ์ ให้ทดสอบ AWS เป็น fallback และ Google V2 เฉพาะหลังยืนยัน Thai diarization ด้วย API จริง OpenAI diarize และ self-hosted Whisper+pyannote ให้เป็น benchmark/fallback ตามข้อจำกัดที่บันทึกไว้ ไม่สลับ provider โดยการแก้ Report layer

งานถัดไปควรเริ่มจากการเพิ่ม `TranscriptionJobs` operational model, กำหนด exact API response สำหรับ asynchronous processing, ทำ audio preflight/metadata validation, สร้าง adapter contract test ที่ใช้ mock provider และเตรียม test fixture แบบ redacted ก่อนสร้าง UI Transcript ขนาดใหญ่ การเพิ่ม operational model นี้เป็นงานรองรับ reliability ของ V1 ไม่ใช่การเพิ่มฟีเจอร์ V2

## References

[1]: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-transcription-create "Azure — Create a batch transcription"
[2]: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits "Azure — Quotas and limits for Speech"
[3]: https://azure.microsoft.com/en-us/pricing/details/speech/ "Azure — Speech pricing"
[4]: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-transcription "Azure — Batch transcription overview"
[5]: https://developers.google.com/apps-script/guides/services/quotas "Google Apps Script — Quotas for Google Services"
[6]: https://docs.cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages "Google Cloud — Cloud Speech-to-Text V2 supported languages"
[7]: https://docs.cloud.google.com/speech-to-text/docs/batch-recognize "Google Cloud — Transcribe long audio files"
[8]: https://docs.cloud.google.com/speech-to-text/docs/quotas "Google Cloud — Quotas and limits"
[9]: https://cloud.google.com/speech-to-text/pricing "Google Cloud — Speech-to-Text pricing"
[10]: https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html "AWS — Supported languages and language-specific features"
[11]: https://docs.aws.amazon.com/transcribe/latest/dg/how-input.html "AWS — Data input and output"
[12]: https://docs.aws.amazon.com/transcribe/latest/dg/diarization.html "AWS — Partitioning speakers (diarization)"
[13]: https://docs.aws.amazon.com/general/latest/gr/transcribe.html "AWS — Amazon Transcribe endpoints and quotas"
[14]: https://developers.openai.com/api/docs/guides/speech-to-text "OpenAI — File transcription"
[15]: https://developers.openai.com/api/docs/models/gpt-4o-transcribe-diarize "OpenAI — GPT-4o Transcribe Diarize model"
[16]: https://github.com/openai/whisper "OpenAI — Whisper repository"
[17]: https://huggingface.co/pyannote/speaker-diarization-community-1 "pyannote — speaker-diarization-community-1 model card"
