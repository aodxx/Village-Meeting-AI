# STT Research Archive — Thai Village Meetings

**วันที่ค้นคว้า:** 2026-08-26
**ขอบเขต:** Speech-to-Text ภาษาไทย, long audio, generic speaker separation และต้นทุน STT
**สถานะ:** Evidence archive สำหรับทีม; decision ล่าสุดอยู่ใน [`docs/FREE-STT-POLICY.md`](../FREE-STT-POLICY.md) และ [`docs/STT-TECHNICAL-SPIKE.md`](../STT-TECHNICAL-SPIKE.md)

## 1. วัตถุประสงค์และวิธีอ่านเอกสาร

เอกสารนี้เก็บหลักฐานจากการค้นคว้าและการทดลองของ Phase 0.1 ไว้ใน Repository เพื่อให้ทีมใช้ประกอบการตัดสินใจได้โดยไม่ต้องเริ่มค้นหาใหม่ทุกครั้ง เอกสารนี้แยก **ข้อเท็จจริงจากแหล่งอ้างอิง**, **ผลการทดลองใน sandbox**, และ **ข้อเสนอเชิงผลิตภัณฑ์** ออกจากกันอย่างชัดเจน

ผลการค้นคว้าไม่ควรถูกอ่านเป็นการรับประกันคุณภาพเสียงประชุมจริง ผู้ให้บริการและ model card อาจรายงานตัวเลขบนชุดข้อมูลมาตรฐานที่แตกต่างจากเสียงหมู่บ้านซึ่งอาจมีสำเนียง เสียงก้อง ระยะไมโครโฟน และการพูดทับกัน ดังนั้นการตัดสิน production ต้องอ้างอิง authorized real-audio benchmark ที่ทีมอนุมัติเท่านั้น

> **Current product constraint:** V1 ต้องไม่ต้องพึ่ง paid Speech-to-Text service สำหรับการใช้งานปกติ การเลือก provider หรือ architecture จึงเปิดกว้าง แต่ default path ต้องไม่สร้าง recurring transcription bill

## 2. Executive findings

จากการค้นคว้า แนวทางที่สอดคล้องกับ cost gate ที่สุดคือ local/open-source pipeline ซึ่งรัน ASR บนเครื่องหรือ runtime ที่โครงการควบคุม โดยไม่ส่งเสียงไปยัง paid STT API โมเดล Thai-specific ที่ถูกนำมาทดสอบคือ `biodatlab/distill-whisper-th-small`; model card ระบุว่าเป็น distilled Whisper สำหรับภาษาไทย, license MIT, ขนาด 0.2B parameters และรายงาน DeepCut-tokenized WER 11.23% บน Common Voice 13 test set [1]

การทดสอบ E2E ใน Repository ใช้โมเดลดังกล่าวสำหรับ Thai transcription, ใช้ `faster-whisper` base + VAD เพื่อแบ่ง speech boundaries และใช้ deterministic pitch-feature clustering เพื่อคืน generic labels `SPEAKER_1`, `SPEAKER_2` โดย `faster-whisper` เป็น implementation แบบ local ที่ใช้ CTranslate2 และเผยแพร่ภายใต้ MIT license [2] ผล smoke test ผ่าน structural checks แต่ยังไม่ใช่ production-quality diarization

แนวทาง paid cloud เช่น Azure, Google Cloud, AWS และ OpenAI มีข้อจำกัดและความสามารถที่เหมาะกับ long audio/diarization ในระดับต่างกัน แต่ถูกเก็บไว้เป็น comparison baseline หรือ optional future fallback เท่านั้น ไม่ใช่ dependency หลักของ V1 ตาม policy [4] [5] [6] [7] [8] [9] [10] [11] [12]

## 3. Evidence matrix

| แนวทาง | หลักฐานที่ค้นพบ | ประโยชน์ต่อโจทย์ | ข้อจำกัด/สิ่งที่ยังไม่พิสูจน์ |
|---|---|---|---|
| `biodatlab/distill-whisper-th-small` | Thai-specific distilled Whisper, MIT, 0.2B parameters; model card รายงาน WER 11.23% บน Common Voice 13 test [1] | ไม่มี STT service fee หลังดาวน์โหลด model; เหมาะเป็น Thai ASR บน local worker | ตัวเลขเป็น model-card benchmark ไม่ใช่เสียงประชุมหมู่บ้าน; ไม่มี diarization ในตัว; ต้องทดสอบสำเนียง/noise/overlap |
| `faster-whisper` | Local Whisper implementation บน CTranslate2, MIT [2] | ใช้ CPU inference/VAD/timestamps และแบ่งไฟล์ยาวเป็นช่วงได้โดยไม่เสียค่าบริการ STT | ความเร็ว/RAM ขึ้นกับ hardware; model conversion บาง checkpoint อาจไม่เข้ากัน; ต้องทำ chunk dedup/restart เอง |
| `pyannote speaker-diarization-community-1` | Local speaker diarization pipeline มี model card และข้อกำหนดการใช้งานของ model [3] | มีโอกาสแยกผู้พูดได้ดีกว่า pitch baseline และรองรับ local processing | ต้องตรวจ model access/license/เงื่อนไขข้อมูล; resource หนักกว่า baseline; ยังไม่ถูก benchmark กับเสียงไทยของโครงการ |
| Azure Speech Batch Standard | เอกสารระบุ batch asynchronous, Thai support, mono diarization, word timestamps และข้อจำกัด 1 GB/240 นาทีเมื่อเปิด diarization [4] [5] | Technical fit สูงสำหรับไฟล์ 1–3 ชั่วโมงและหลายผู้พูด | เป็น paid service; ต้องมี provider staging และค่าใช้จ่ายต่อชั่วโมง; ไม่ใช่ default ภายใต้ V1 policy |
| Google Cloud Speech-to-Text V2 | มี Thai models/locale และ batch recognition ผ่าน Cloud Storage; quotas และราคาต้องอ่านร่วมกับ model/region [6] [7] [8] [9] | เข้ากับ Google ecosystem และ long-running operation | Thai diarization capability ต้องยืนยันด้วย compatibility probe; มีค่าใช้บริการและ GCS staging |
| Amazon Transcribe | language table รองรับ Thai; batch input/output ผ่าน S3 และ speaker labels/diarization มีข้อกำหนดเฉพาะ [10] [11] [12] [13] | รองรับไฟล์ยาวและ generic speaker labels ใน technical contract | เป็น paid service; ต้องมี S3/IAM; ราคา tier/region ไม่ควรสรุปจาก high-volume example |
| OpenAI transcription/diarize | guide ระบุ file limit 25 MB และ diarized JSON/segment timestamps สำหรับ model ที่รองรับ [14] [15] | มี diarization และ transcript quality ที่ควรเก็บไว้เป็น benchmark | ไฟล์ประชุม 1–3 ชั่วโมงต้อง chunk/dedupe; diarize model มีข้อจำกัด realtime/prompt และคิดตาม usage |
| Google Apps Script เป็น orchestration | Apps Script quotas ระบุ runtime สูงสุด 6 นาทีต่อ execution และ URL Fetch payload/response limits [16] | เหมาะกับการสร้าง job, persist state และ poll worker | ไม่เหมาะกับการรัน Whisper หรือรอถอดเสียงยาวใน HTTP request เดียว |

## 4. Local E2E experiment recorded in Repository

### 4.1 Pipeline

ต้นแบบที่รันจริงอยู่ใต้ [`tools/free_stt_spike/`](../../tools/free_stt_spike/) และมี README/requirements/fixture generator/evaluator แยกไว้แล้ว pipeline มีลำดับดังนี้:

```text
synthetic Thai fixture
        |
        v
faster-whisper base + VAD  -> speech boundaries/timestamps
        |
        v
biodatlab/distill-whisper-th-small -> Thai text per boundary
        |
        v
pitch features + deterministic clustering -> generic speaker labels
        |
        v
normalized JSON: speaker/startMs/endMs/text
```

โมเดลและ inference ทำงาน local หลังดาวน์โหลด checkpoint ครั้งแรก ไม่มีการเรียก paid STT API และไม่มี STT service fee ต่อการรัน การสร้าง synthetic fixture ใช้ TTS เพื่อทดสอบ plumbing เท่านั้น ไม่ใช่ runtime STT และไม่ใช่เสียงประชุมจริง

### 4.2 Fixture and measured result

fixture เป็นเสียงภาษาไทยสังเคราะห์สองผู้พูด ความยาวประมาณ 38.4 วินาที ไม่มีข้อมูลส่วนตัวหรือเสียงประชุมจริง ผล canonical อยู่ที่ [`thai_specific_segmented.json`](../../tools/free_stt_spike/results/thai_specific_segmented.json) และผลตรวจสอบอยู่ที่ [`thai_specific_segmented_evaluation.json`](../../tools/free_stt_spike/results/thai_specific_segmented_evaluation.json)

| Metric | Observed result |
|---|---:|
| STT service fee | `0` |
| Detected language | `th` |
| Normalized segments | `4/4` ผ่าน |
| Timestamp validity | ผ่าน |
| Speaker order | `1,2,1,2` ผ่าน |
| Average CER proxy | `0.1611` |
| Clean-run processing time | ประมาณ `43.963` วินาทีบน CPU sandbox |

ผลนี้ยืนยันว่า local worker สามารถอ่านเสียง, คืน timestamp, คืนข้อความไทย, map generic speakers และ serialize ผลลัพธ์ตาม contract ได้ครบ แต่ **ไม่ยืนยันคุณภาพการถอดเสียงจริง** ค่า CER proxy มาจาก synthetic fixture และ speaker labels มาจาก pitch baseline ซึ่งยังไม่แทน trained diarization

### 4.3 Compatibility observation

มีการทดลองแปลง Thai-specific checkpoint เป็น CTranslate2 เพื่อใช้ inference ผ่าน faster-whisper โดยตรง แต่เกิด segmentation fault ใน environment ของ spike ทั้งแบบ quantized และ float32 จึงเลือกใช้ Transformers สำหรับ Thai ASR และใช้ faster-whisper base เฉพาะ boundary detection ในผลที่ commit ไว้ การ optimize conversion เป็นงาน compatibility แยก ไม่ควรทำให้ทีมเข้าใจว่า local approach ใช้ไม่ได้

## 5. Constraints that matter for team decisions

### 5.1 Long audio

ผล 38.4 วินาทีไม่สามารถยืนยันการรองรับ 1–3 ชั่วโมงได้ การนำ local pipeline ไปใช้กับไฟล์ยาวต้องเพิ่ม bounded chunking, global offsets, overlap policy, duplicate suppression, progress persistence และ restart/retry semantics การวัดที่ต้องเก็บคือ wall time, model load time, peak RAM, disk, chunk count, failure point และเวลาที่กลับมาทำต่อได้

### 5.2 Speaker separation

Speaker diarization เป็นความสามารถเสริม ไม่ใช่ cost gate ของ V1 หาก text quality ดีแต่ speaker separation ไม่น่าเชื่อถือ V1 ควรลด/ถอด generic speaker labels แล้วส่ง transcript ให้มนุษย์ review แทนการบังคับใช้ paid diarization การแสดง `SPEAKER_1` จาก baseline ต้องระบุว่าเป็น generic label ภายใน meeting เดียว ไม่ใช่ชื่อหรือ voice identity

### 5.3 Live transcription

Live transcription ควรเป็น preview และอาจลดหรือเลื่อนได้หากทำให้ต้องใช้ paid infrastructure หรือทำให้ reliability แย่ลง POST transcript หลังจบประชุมต้องเป็น authoritative input สำหรับ AI analysis และ Final Report โดย Final Report ยังคงเป็น snapshot และ public report ต้องอ่านจาก Final Report เท่านั้น

### 5.4 Cost boundary

คำว่า zero-STT-fee หมายถึงไม่มีค่าบริการ STT ต่อ audio minute/hour สำหรับ normal V1 operation ไม่ได้หมายความว่า compute, disk, network, model download, runtime hosting หรือการสร้าง TTS fixture เป็นศูนย์ ต้นทุนแฝงและ resource ต้องถูกบันทึกใน `TranscriptionJobs` หรือ benchmark artifact โดยไม่เก็บ secret หรือ private meeting audio ลง GitHub

## 6. Decision record

| คำถาม | ข้อสรุปปัจจุบัน |
|---|---|
| V1 ต้องมี paid STT หรือไม่ | ไม่ต้องมี; ห้ามเพิ่มเป็น required dependency |
| Primary candidate หลัง E2E spike | Local Thai STT worker ตาม pipeline ใน Section 4 |
| Provider lock-in | ไม่มี; `SpeechToTextAdapter` ต้องรับ local/open-source/browser/free-tier/future paid implementations ได้ |
| Diarization | Optional; baseline ใน spike ยังไม่ผ่าน production quality gate |
| Live mode | Optional preview; อาจลด/เลื่อนเพื่อรักษา zero-cost/reliability |
| Final Report | ต้องใช้ transcript ที่ผ่าน processing/review และยังคง snapshot semantics |
| Paid providers | comparison/future optional fallback เท่านั้น; ห้ามสลับอัตโนมัติและต้องมี explicit product decision |

## 7. Recommended reading order for the team

เริ่มจาก [`docs/FREE-STT-POLICY.md`](../FREE-STT-POLICY.md) เพื่อเข้าใจกติกา product จากนั้นอ่าน [`docs/STT-TECHNICAL-SPIKE.md`](../STT-TECHNICAL-SPIKE.md) เพื่อดู comparison และ decision rationale อ่าน [`docs/ZERO-COST-STT-NEXT-STEP.md`](../ZERO-COST-STT-NEXT-STEP.md) เพื่อดู benchmark backlog แล้วตรวจผลรันจริงใน [`tools/free_stt_spike/README.md`](../../tools/free_stt_spike/README.md) และ evaluator JSON

## References

[1]: https://huggingface.co/biodatlab/distill-whisper-th-small "Biodatlab — distill-whisper-th-small model card"
[2]: https://github.com/SYSTRAN/faster-whisper "SYSTRAN — faster-whisper"
[3]: https://huggingface.co/pyannote/speaker-diarization-community-1 "pyannote — speaker-diarization-community-1 model card"
[4]: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-transcription-create "Azure — Create a batch transcription"
[5]: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits "Azure — Quotas and limits for Speech"
[6]: https://docs.cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages "Google Cloud — Supported languages"
[7]: https://docs.cloud.google.com/speech-to-text/docs/batch-recognize "Google Cloud — Batch recognize"
[8]: https://docs.cloud.google.com/speech-to-text/docs/quotas "Google Cloud — Quotas and limits"
[9]: https://cloud.google.com/speech-to-text/pricing "Google Cloud — Speech-to-Text pricing"
[10]: https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html "AWS — Supported languages"
[11]: https://docs.aws.amazon.com/transcribe/latest/dg/how-input.html "AWS — Data input and output"
[12]: https://docs.aws.amazon.com/transcribe/latest/dg/diarization.html "AWS — Speaker labels and diarization"
[13]: https://docs.aws.amazon.com/general/latest/gr/transcribe.html "AWS — Amazon Transcribe quotas and endpoints"
[14]: https://developers.openai.com/api/docs/guides/speech-to-text "OpenAI — Speech-to-text guide"
[15]: https://developers.openai.com/api/docs/models/gpt-4o-transcribe-diarize "OpenAI — GPT-4o Transcribe Diarize"
[16]: https://developers.google.com/apps-script/guides/services/quotas "Google Apps Script — Quotas"
