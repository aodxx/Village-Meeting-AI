#!/usr/bin/env python3
"""Generate an optional public-service TTS fixture for local STT smoke tests.

This is not a meeting recording and must not be used as a quality benchmark.
The generated audio is disposable test data, not a project record.
"""

from pathlib import Path
import json
import subprocess

from gtts import gTTS

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "fixtures" / ".gtts-work"
OUT = ROOT / "fixtures" / "thai_two_speaker_gtts.wav"
MANIFEST = ROOT / "fixtures" / "thai_two_speaker_gtts.json"
WORK.mkdir(parents=True, exist_ok=True)
for path in WORK.glob("*.mp3"):
    path.unlink()

lines = [
    ("a1", "สวัสดีครับ วันนี้เราจะประชุมเรื่องน้ำประปาของหมู่บ้าน", "0"),
    ("b1", "ขอเสนอให้ตรวจสอบถังเก็บน้ำและบันทึกปัญหาที่พบ", "-700"),
    ("a2", "ที่ประชุมควรกำหนดวันซ่อมและติดตามผลในสัปดาห์หน้า", "0"),
    ("b2", "รับทราบค่ะ ขอให้ผู้รับผิดชอบแจ้งความคืบหน้าต่อที่ประชุม", "-700"),
]

for stem, text, pitch in lines:
    mp3 = WORK / f"{stem}.mp3"
    gTTS(text=text, lang="th", slow=False).save(str(mp3))
    wav = WORK / f"{stem}.wav"
    filter_chain = "aresample=16000,asetrate=16000" if pitch == "0" else f"asetrate=16000*{2 ** (int(pitch) / 1200):.8f},aresample=16000"
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(mp3), "-af", filter_chain, "-ar", "16000", "-ac", "1", str(wav)],
        check=True,
    )

silence = WORK / "silence.wav"
subprocess.run(
    ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono", "-t", "0.8", str(silence)],
    check=True,
)
concat = WORK / "concat.txt"
concat.write_text("\n".join(f"file '{WORK / (stem + '.wav')}'\nfile '{silence}'" for stem, _, _ in lines[:-1]) + f"\nfile '{WORK / 'b2.wav'}'\n", encoding="utf-8")
subprocess.run(
    ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(OUT)],
    check=True,
)
MANIFEST.write_text(
    json.dumps(
        {
            "fixtureId": "thai_two_speaker_gtts_v2",
            "kind": "synthetic",
            "purpose": "local STT adapter smoke test; not a meeting quality benchmark",
            "language": "th",
            "expectedSpeakerCount": 2,
            "expectedOrder": ["SPEAKER_A", "SPEAKER_B", "SPEAKER_A", "SPEAKER_B"],
            "expectedTexts": [text for _, text, _ in lines],
            "privacy": "no real meeting or personal data",
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print(OUT)
