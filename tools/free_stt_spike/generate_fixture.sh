#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
FIXTURE_DIR="$ROOT/fixtures"
WORK_DIR="$FIXTURE_DIR/.work"
mkdir -p "$WORK_DIR"
rm -f "$WORK_DIR"/*.wav "$FIXTURE_DIR/thai_two_speaker_smoke.wav" "$FIXTURE_DIR/thai_two_speaker_smoke.json"

# Synthetic speech is used only to test the adapter contract and local
# execution. It is not a substitute for a licensed real village recording.
espeak-ng -v th+m3 -s 145 -p 25 -w "$WORK_DIR/a1.wav" \
  "สวัสดีครับ วันนี้เราจะประชุมเรื่องน้ำประปาของหมู่บ้าน"
espeak-ng -v th+f2 -s 145 -p 75 -w "$WORK_DIR/b1.wav" \
  "ขอเสนอให้ตรวจสอบถังเก็บน้ำและบันทึกปัญหาที่พบ"
espeak-ng -v th+m3 -s 145 -p 25 -w "$WORK_DIR/a2.wav" \
  "ที่ประชุมควรกำหนดวันซ่อมและติดตามผลในสัปดาห์หน้า"
espeak-ng -v th+f2 -s 145 -p 75 -w "$WORK_DIR/b2.wav" \
  "รับทราบค่ะ ขอให้ผู้รับผิดชอบแจ้งความคืบหน้าต่อที่ประชุม"

ffmpeg -hide_banner -loglevel error -f lavfi -i anullsrc=r=16000:cl=mono -t 0.8 "$WORK_DIR/silence.wav"
cat > "$WORK_DIR/concat.txt" <<EOF
file '$WORK_DIR/a1.wav'
file '$WORK_DIR/silence.wav'
file '$WORK_DIR/b1.wav'
file '$WORK_DIR/silence.wav'
file '$WORK_DIR/a2.wav'
file '$WORK_DIR/silence.wav'
file '$WORK_DIR/b2.wav'
EOF
ffmpeg -hide_banner -loglevel error -f concat -safe 0 -i "$WORK_DIR/concat.txt" \
  -ar 16000 -ac 1 -c:a pcm_s16le "$FIXTURE_DIR/thai_two_speaker_smoke.wav"

cat > "$FIXTURE_DIR/thai_two_speaker_smoke.json" <<'EOF'
{
  "fixtureId": "thai_two_speaker_smoke_v1",
  "kind": "synthetic",
  "purpose": "local adapter end-to-end smoke test only",
  "language": "th",
  "expectedSpeakerCount": 2,
  "expectedOrder": ["SPEAKER_A", "SPEAKER_B", "SPEAKER_A", "SPEAKER_B"],
  "speakerConstruction": {
    "SPEAKER_A": "espeak-ng th+m3",
    "SPEAKER_B": "espeak-ng th+f2"
  },
  "privacy": "no real meeting or personal data"
}
EOF
rm -rf "$WORK_DIR"
printf 'created %s\n' "$FIXTURE_DIR/thai_two_speaker_smoke.wav"
