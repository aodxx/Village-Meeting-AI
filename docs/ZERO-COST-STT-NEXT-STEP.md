# Zero-Cost STT — Next Step

**Phase:** 0.1 continuation
**วันที่:** 2026-08-26
**สถานะ:** E2E smoke test passed; real-meeting and long-audio gates open

## Current decision

ให้เดินหน้าด้วย **local Thai STT worker** เป็นเส้นทางหลักของ V1 ในช่วงถัดไป โดยไม่ผูกกับ paid STT provider และยังคง `SpeechToTextAdapter` เป็น boundary กลาง โมเดลที่ใช้ในต้นแบบคือ `biodatlab/distill-whisper-th-small` สำหรับ Thai ASR ซึ่งมี model card ระบุว่าเป็น Thai-specific checkpoint และเผยแพร่ภายใต้ MIT license [1] ส่วน `faster-whisper` ใช้สร้าง speech boundaries/VAD และเผยแพร่ภายใต้ MIT license [2]

การเลือกนี้ผ่านการทดสอบแบบ end-to-end บน CPU ด้วย synthetic Thai fixture โดยไม่มี STT service call และคืนผล normalized segments กับ generic speaker order ได้ครบ อย่างไรก็ตาม speaker separation ในต้นแบบเป็น deterministic pitch-feature clustering เท่านั้น ไม่ใช่ trained diarization จึงยังไม่สามารถอ้างว่าเหมาะกับเสียงประชุมหมู่บ้านจริงหรือการพูดทับกันได้

## Immediate next step

ขั้นถัดไปคือสร้าง **authorized real-audio benchmark harness** โดยไม่สร้าง UI ขนาดใหญ่และไม่ส่งเสียงประชุมไปยัง paid STT API ชุดทดสอบต้องมีเจ้าของข้อมูลอนุมัติการใช้และการลบอย่างชัดเจน และควรจัดเก็บภายใต้ `VillageMeetingAI/90-Tests/` เมื่อจำเป็นต้องใช้ Google Drive runtime artifact เท่านั้น ไม่เก็บเสียงจริงไว้ใน GitHub

| ลำดับ | งาน | ผลลัพธ์ที่ต้องบันทึก | Exit condition |
|---:|---|---|---|
| 1 | ขอ/เตรียม audio fixture ที่ได้รับอนุญาต | duration, sample rate, channels, size, consent/data-retention note | มีคลิป 2 ผู้พูดและหลายผู้พูด; ไม่มีข้อมูลเกินวัตถุประสงค์ |
| 2 | ทำ audio preflight | mono/stereo, sample rate, codec, silence/noise metadata | worker ปฏิเสธไฟล์ที่ไม่รองรับด้วย error ที่อ่านได้ |
| 3 | รัน local Thai ASR | model revision, runtime, command, processing time, transcript | transcript มี start/end และข้อความที่ตรวจสอบย้อนกลับได้ |
| 4 | benchmark speaker separation | human-labeled speaker turns, generic label mapping, overlap cases | รายงาน diarization error/coverage แยกจาก ASR CER/WER |
| 5 | benchmark 1–3 ชั่วโมง | peak RAM, disk, wall time, chunk count, retry/restart behavior | worker กลับมาทำต่อได้หลังหยุด และไม่สร้าง duplicate segments |
| 6 | integration contract test | normalized JSON, `TranscriptionJobs`, error codes, idempotency key | Apps Script ไม่ต้องรัน inference และไม่ busy-wait |
| 7 | quality review | human corrections, unsupported words, hallucination/omission examples | ตัดสินว่า baseline ผ่าน/ไม่ผ่านโดยมีหลักฐาน ไม่เดาแทนข้อมูล |

## Required engineering changes before UI

ควรเพิ่ม local worker interface ให้รับ input เป็น `MeetingID`, canonical audio reference, `languageCode`, `expectedSpeakerRange`, `modelVersion` และ `idempotencyKey` แล้วคืน `status`, `segments`, `metrics` และ typed error ผล `segments` ต้องตรงกับ `docs/API-CONTRACT.md` และ persist ผ่าน `TranscriptionJobs` ตาม `docs/DATA-MODEL.md`

Worker ต้องแบ่งไฟล์ยาวเป็น bounded chunks โดยเก็บ global offset และ overlap policy อย่างชัดเจน การ deduplicate ต้องทำเฉพาะขอบ chunk ที่ยืนยันซ้ำได้ หากไม่มั่นใจให้เก็บ segment ไว้สำหรับ human review แทนการลบหลักฐาน การเปลี่ยน speaker label ต้อง stable เฉพาะภายใน Meeting เดียว และห้ามตีความเป็นชื่อบุคคล

Apps Script ต้องทำหน้าที่สร้าง job, ตรวจสิทธิ์/metadata, บันทึก state, สั่ง worker, poll ผล และ persist normalized segments ส่วนการประมวลผล Python/Whisper ต้องอยู่นอก Apps Script execution การออกแบบนี้สอดคล้องกับข้อจำกัดของ Apps Script ที่ execution สูงสุด 6 นาที และ URL Fetch POST/response สูงสุด 50 MB ต่อ call [3]

## No automatic paid fallback

ถ้า local worker ไม่พร้อม, model โหลดไม่ได้, RAM ไม่พอ หรือ diarization quality ไม่ผ่าน ระบบต้องคืน error ที่ชัดเจน เช่น `TRANSCRIPTION_WORKER_UNAVAILABLE` หรือ `TRANSCRIPTION_RESOURCE_EXHAUSTED` และรักษา canonical audio/job state ไว้เพื่อ retry ห้ามสลับไป Azure, Google, AWS หรือ OpenAI โดยอัตโนมัติ เพราะจะขัดกับ zero-STT-fee policy และอาจสร้างค่าใช้จ่ายโดยผู้ใช้ไม่ทันยืนยัน

Paid provider อาจถูกทดสอบเป็น benchmark แยกในอนาคตได้ก็ต่อเมื่อมี product approval, budget boundary, data-transfer review และการบันทึก cost class แยกจาก local path การทดสอบนั้นต้องไม่เปลี่ยน public/report contract

## Definition of done for the next step

งานถัดไปจะถือว่าผ่านเมื่อมีเสียงจริงที่ได้รับอนุญาตอย่างน้อยหนึ่งชุดสำหรับการตรวจคุณภาพ, local worker ประมวลผลได้แบบไม่เสีย STT fee, ผลลัพธ์ normalize และ persist ได้, speaker limitation ถูกเปิดเผยตรงไปตรงมา, long-audio failure/retry ถูกทดสอบ และ `PROGRESS.md` ระบุผลผ่าน/ไม่ผ่านพร้อมหลักฐาน ก่อนเริ่ม UI ขนาดใหญ่ต้องมีการตัดสินใจที่ชัดเจนว่า baseline local diarization เพียงพอสำหรับ V1 หรือจำเป็นต้องเลื่อน human review มาเป็น gate

## References

[1]: https://huggingface.co/biodatlab/distill-whisper-th-small "Biodatlab — distill-whisper-th-small model card"
[2]: https://github.com/SYSTRAN/faster-whisper "SYSTRAN — faster-whisper"
[3]: https://developers.google.com/apps-script/guides/services/quotas "Google Apps Script — Quotas for Google Services"
