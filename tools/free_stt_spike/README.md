# Free Thai STT Spike

ต้นแบบนี้พิสูจน์แนวทาง **local-only STT** สำหรับ Phase 0.1 โดยไม่เรียก paid STT API และไม่มีค่า STT ต่อ audio minute ระหว่างการรัน โมเดลถูกดาวน์โหลดจาก Hugging Face ครั้งแรกแล้วรันบน CPU ในเครื่อง

## Architecture

ต้นแบบใช้สองชั้นที่แยก responsibility กัน:

| ชั้น | วิธี | หน้าที่ |
|---|---|---|
| Speech boundaries | `faster-whisper` multilingual `base` + VAD | ตรวจช่วงเสียงพูดและคืน start/end timestamp |
| Thai transcription | `biodatlab/distill-whisper-th-small` ผ่าน Transformers | ถอดข้อความภาษาไทยในแต่ละช่วง |
| Generic speaker labels | deterministic pitch-feature KMeans baseline | map เป็น `SPEAKER_1`, `SPEAKER_2` ภายใน meeting เดียว |
| Normalization | local adapter | คืน `{ speaker, startMs, endMs, text }` โดยไม่เปิดเผย provider-specific response |

การแยก speaker ในต้นแบบเป็น **baseline diarization ไม่ใช่ production-quality diarization** เนื่องจากใช้ acoustic pitch features และกำหนดจำนวนผู้พูดที่คาดไว้ล่วงหน้า การประชุมจริงที่มีเสียงก้อง การพูดทับกัน สำเนียงต่างกัน หรือไมโครโฟนตัวเดียวต้อง benchmark กับ diarization model โดยเฉพาะก่อนใช้งานจริง

## Install

```bash
sudo pip3 install faster-whisper torch transformers sentencepiece soundfile gTTS
```

โมเดล `biodatlab/distill-whisper-th-small` เป็น Thai-specific model ที่ใช้ license MIT ตาม model card และมีรายงาน WER 11.23% บน Common Voice 13 test set โดยเจ้าของโมเดล [1] `faster-whisper` เป็น implementation ของ Whisper ที่ใช้ CTranslate2 และเผยแพร่ภายใต้ MIT license [2]

## End-to-end smoke test

คำสั่งต่อไปนี้สร้าง fixture ภาษาไทยแบบสังเคราะห์ที่ไม่มีข้อมูลส่วนตัว แล้วรัน local adapter และ evaluator:

```bash
cd /home/ubuntu/Village-Meeting-AI
python3 tools/free_stt_spike/generate_gtts_fixture.py
python3 tools/free_stt_spike/thai_specific_segmented_adapter.py \
  tools/free_stt_spike/fixtures/thai_two_speaker_gtts.wav \
  --output tools/free_stt_spike/results/thai_specific_segmented.json \
  --expected-speakers 2
python3 tools/free_stt_spike/evaluate_result.py \
  tools/free_stt_spike/fixtures/thai_two_speaker_gtts.json \
  tools/free_stt_spike/results/thai_specific_segmented.json \
  --output tools/free_stt_spike/results/thai_specific_segmented_evaluation.json
```

ผลการรันที่บันทึกใน `results/thai_specific_segmented_evaluation.json`:

| Check | ผล |
|---|---:|
| STT fee | `0` |
| Detected language | `th` |
| Normalized segments | `4/4` ผ่าน |
| Speaker order | `SPEAKER_1, SPEAKER_2, SPEAKER_1, SPEAKER_2` ผ่าน |
| Average CER proxy | `0.1611` |
| Processing time | ประมาณ 35.6 วินาที บน sandbox CPU สำหรับเสียงประมาณ 38.4 วินาที |

CER proxy นี้คำนวณจาก synthetic TTS fixture ที่ข้อความอ้างอิงถูกสร้างโดยสคริปต์เดียวกัน จึงเป็นเพียง smoke-test metric ไม่ใช่ผลคาดการณ์เสียงประชุมจริง เสียงที่สร้างด้วย TTS ยังไม่สะท้อน noise, room echo, overlap หรือสำเนียงท้องถิ่น

## Reproducibility and data policy

ไฟล์ `fixtures/thai_two_speaker_gtts.wav` และ manifest เป็น synthetic test data ไม่มีเสียงประชุมจริงหรือข้อมูลส่วนตัว จึงเก็บใน Repository ได้ ส่วน model cache, temporary segment WAV และผลทดลองที่ไม่ใช่ canonical result ต้องไม่ commit และควรลบก่อนใช้งานจริง

ห้ามนำ adapter นี้ไปตีความชื่อผู้พูดหรือยืนยันมติเอง ผลลัพธ์เป็น transcript segments เท่านั้น และต้องผ่าน human review กับกฎ Final Report snapshot ของโครงการ

## Known limitations

ต้นแบบนี้ยังไม่ใช่ระบบรองรับไฟล์ 1–3 ชั่วโมงแบบ production เนื่องจากยังไม่มี long-file chunk scheduler, persisted job state, resumable upload, overlap deduplication หรือ trained diarization pipeline ที่ผ่านชุดเสียงจริง การประมวลผลบน CPU มี latency สูงขึ้นตามความยาวเสียง และต้องจัดสรร RAM/disk สำหรับ model cache

โมเดล Thai-specific checkpoint ทำงานแบบ Transformers ได้ แต่การแปลงเป็น CTranslate2 เพื่อใช้กับ faster-whisper เกิด segmentation fault ใน environment นี้ จึงเลือกใช้ Transformers สำหรับ transcription และใช้ faster-whisper base เฉพาะ boundary detection ใน spike นี้ ปัญหาดังกล่าวต้องแยกเป็น compatibility task หากจะ optimize inference ภายหลัง

## References

[1]: https://huggingface.co/biodatlab/distill-whisper-th-small "Biodatlab — distill-whisper-th-small model card"
[2]: https://github.com/SYSTRAN/faster-whisper "SYSTRAN — faster-whisper"
