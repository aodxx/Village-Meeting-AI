# Free STT Policy — Village Meeting AI

**สถานะ:** Active for Phase 0.1 continuation
**วันที่:** 2026-08-26
**ขอบเขต:** V1 Speech-to-Text only

## 1. Purpose

เอกสารนี้กำหนดกติกาสำหรับแนวทาง Speech-to-Text ที่ไม่มีค่าบริการ STT ตามเป้าหมาย Phase 0.1 ของโครงการ คำว่า **zero-STT-fee** หมายถึงระบบต้องไม่ส่งเสียงประชุมไปยัง paid Speech-to-Text API และต้องไม่มีค่าใช้บริการ STT ต่อ audio minute ในเส้นทางหลักของ V1 ไม่ได้หมายความว่าค่าไฟฟ้า เครื่องผู้ใช้ พื้นที่เก็บข้อมูล bandwidth หรือค่าแรงดูแลระบบเป็นศูนย์

กติกานี้ไม่เปลี่ยนเป้าหมาย V1 เรื่องการบันทึกเสียง ถอดเสียง แยกผู้พูดแบบ generic labels วิเคราะห์ และสร้าง Final Report ที่มนุษย์ตรวจสอบได้ และไม่เพิ่ม voice identity, voting หรือฟีเจอร์ V2

## 2. Policy decisions

ไม่มี provider หรือ architecture ใดถูกล็อกไว้ล่วงหน้า แนวทางที่อนุญาตรวมถึง open-source/local, on-device, browser/WebAssembly/WebGPU, self-hosted, free compute/free notebook, free-tier ที่ไม่บังคับ billing, hybrid และ chunked post-meeting processing ตราบเท่าที่ normal V1 operation ไม่ต้องจ่าย STT service fee

| กติกา | ข้อกำหนด |
|---|---|
| Local-first | เส้นทางหลักต้องรัน ASR/segmentation บนเครื่องหรือ runtime ที่โครงการควบคุม โดยไม่เรียก paid STT service |
| Paid fallback | ห้ามสลับไป paid provider อัตโนมัติเมื่อ local worker ล้มเหลว ต้องมี product/operations approval และบันทึก cost class ของ job |
| Provider-neutral | ทุกวิธีต้องอยู่หลัง `SpeechToTextAdapter` และคืน normalized segments ชุดเดียวกัน |
| Data residency | ต้นฉบับอยู่ใต้ Google Drive root `VillageMeetingAI/02-Audio-Temp/`; ห้ามสร้าง Project Root ใหม่; test assets อยู่ `VillageMeetingAI/90-Tests/` เมื่อใช้ Drive runtime |
| Secrets | ห้ามใส่ token, key, credential หรือ private meeting audio ใน GitHub, Drive document, log หรือ fixture ที่ commit |
| Speaker semantics | ใช้ `SPEAKER_1`, `SPEAKER_2`, ... เฉพาะภายใน meeting เดียว; ห้ามกล่าวว่าเป็นบุคคลจริงหรือทำ voice identity |
| Diarization priority | เป็น desirable/optional; ไม่ใช่ blocker หากทำให้ต้องพึ่ง paid serviceหรือทำให้ความน่าเชื่อถือแย่ลง |
| Live priority | เป็น secondary preview; ลดหรือเลื่อนได้หากขัดกับ zero-cost หรือ reliability |
| Evidence safety | ห้ามแก้คำพูดหรือเติม fact ให้ transcript; ค่าไม่แน่ใจต้องส่ง human review และ AI ห้ามยืนยันมติแทนมนุษย์ |
| Report authority | POST transcript ที่ผ่าน processing/review เป็น authoritative input; LIVE เป็น preview และต้องไม่สร้าง Final Report จาก partial state |
| Reproducibility | ต้องบันทึก model revision, runtime/config, audio metadata, command, result และข้อจำกัด โดยไม่บันทึกข้อมูลลับ |

## 3. Allowed zero-STT-fee approaches

แนวทางใดก็ตามที่ไม่มี paid STT service เป็นข้อบังคับสามารถใช้เป็นเส้นทางหลักได้ โดย local/open-source ที่รันบน CPU/GPU ของผู้ใช้หรือ runtime ที่ผู้ใช้ควบคุมเป็น candidate ปัจจุบัน โมเดล Thai-specific ที่นำมาทดสอบใน Phase 0.1 คือ `biodatlab/distill-whisper-th-small` ซึ่ง model card ระบุ license MIT และเป็นโมเดลที่ fine-tune สำหรับภาษาไทย [1] การประมวลผลและ model cache ต้องอยู่ใน local worker ไม่ใช่ Apps Script execution

`faster-whisper` ใช้เป็น local speech-boundary/ASR runtime ได้ โดย project ระบุว่าเป็น reimplementation ของ Whisper ที่ใช้ CTranslate2 และมี license MIT [2] หากใช้ diarization toolkit เช่น pyannote ต้องตรวจ license, model access conditions และการส่ง telemetry/ข้อมูลทุกครั้งก่อนนำไปใช้กับเสียงประชุมจริง [3]

การสร้าง synthetic fixture ด้วย TTS เพื่อทดสอบ plumbing เป็นข้อยกเว้นที่อนุญาต เพราะไม่ใช่ STT runtime และ fixture ที่ commit ต้องไม่มีข้อมูลบุคคลหรือการประชุมจริง การใช้ fixture สังเคราะห์ห้ามถูกตีความว่าเป็นหลักฐานคุณภาพสำหรับสำเนียง เสียงรบกวน หรือการพูดทับกันในสถานที่จริง

## 4. Quality and safety gates

ต้นแบบจะถือว่า **E2E smoke-test passed** เมื่อไม่มี paid STT call, ตรวจพบภาษาไทย, คืน normalized segments ที่มี `speaker`, `startMs`, `endMs`, `text`, timestamp ถูกต้อง, speaker labels ไม่ใช่ชื่อจริง และผลสามารถบันทึกเป็น JSON ที่ทำซ้ำได้

ต้นแบบจะยังไม่ถือว่า **production quality passed** จนกว่าจะทดสอบด้วยเสียงภาษาไทยที่ผู้ใช้มีสิทธิ์ให้ทดสอบและลบได้ ซึ่งต้องครอบคลุมหลายผู้พูด เสียงก้อง/รบกวน การพูดทับกัน ความยาว 1 ชั่วโมงและ 3 ชั่วโมง การหยุด worker การ retry และการตรวจความถูกต้องของ transcript โดยมนุษย์

ความถูกต้องของข้อความและ speaker separation ต้องรายงานแยกกัน การมี timestamp หรือ speaker label ครบไม่ได้แปลว่าเนื้อความถูกต้อง และค่า CER/WER จาก synthetic fixture เป็นเพียง diagnostic ไม่ใช่ SLA หาก free approach ให้ข้อความดีแต่แยกผู้พูดไม่น่าเชื่อถือ V1 อาจใช้ข้อความโดยลด/ถอด speaker labels และใช้ human review แทน ห้ามให้ AI สรุปมติหรือกำหนดผู้รับผิดชอบจากข้อความที่ยังไม่ผ่าน review

## 5. Cost and operations boundary

`sttFee=0` ต้องเป็น property ที่ตรวจได้ในผล adapter และผลทดสอบต้องระบุค่าใช้จ่ายแฝงที่ยังมีอยู่ ได้แก่ CPU/GPU time, RAM/disk สำหรับ model cache, network สำหรับดาวน์โหลด model ครั้งแรก, TTS cost/terms หากใช้สร้าง fixture และค่า runtime ที่ผู้ใช้เลือกเอง

Apps Script ทำหน้าที่ orchestration และ persistence เท่านั้น ไม่รัน Python/Whisper ใน execution เดียวกับ HTTP request ระบบต้องรองรับ job state, refresh, retry และ worker unavailable โดยไม่เปลี่ยน Meeting state ผิดลำดับ และไม่สลับ paid provider อัตโนมัติ

## 6. Change control

การเปลี่ยน local model, diarization method หรือการเพิ่ม fallback provider ต้องอัปเดต `docs/STT-TECHNICAL-SPIKE.md`, `docs/ZERO-COST-STT-NEXT-STEP.md`, `docs/ARCHITECTURE.md` และ `PROGRESS.md` พร้อมผลทดสอบที่เกี่ยวข้อง หากข้อเสนอใหม่มีผลต่อ schema หรือ state transition ต้องอัปเดต `docs/DATA-MODEL.md` และ `docs/API-CONTRACT.md` ใน commit เดียวกัน

## References

[1]: https://huggingface.co/biodatlab/distill-whisper-th-small "Biodatlab — distill-whisper-th-small model card"
[2]: https://github.com/SYSTRAN/faster-whisper "SYSTRAN — faster-whisper"
[3]: https://huggingface.co/pyannote/speaker-diarization-community-1 "pyannote — speaker-diarization-community-1 model card"
