#!/usr/bin/env python3
"""Thai-specific local ASR adapter with timestamped segmentation.

The base faster-whisper pass supplies speech boundaries. Each boundary is
then transcribed by a Thai fine-tuned Whisper checkpoint. This keeps the
normalized contract stable and is intentionally a spike, not a production
diarizer.
"""

from __future__ import annotations

import argparse
import json
import time
import wave
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
from faster_whisper import WhisperModel
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from free_stt_adapter import LocalWhisperAdapter

THAI_MODEL_ID = "biodatlab/distill-whisper-th-small"
CACHE_DIR = Path("tools/free_stt_spike/cache")


def pitch_features(audio_path: Path, segments: list) -> np.ndarray:
    with wave.open(str(audio_path), "rb") as handle:
        sample_rate = handle.getframerate()
        samples = np.frombuffer(handle.readframes(handle.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    rows = []
    for segment in segments:
        start = max(0, int(segment.start * sample_rate))
        end = min(len(samples), max(start + 1, int(segment.end * sample_rate)))
        window = samples[start:end]
        window = window - float(np.mean(window))
        rms = float(np.sqrt(np.mean(window * window))) if len(window) else 0.0
        min_lag = max(1, int(sample_rate / 350))
        max_lag = min(len(window) - 1, int(sample_rate / 70))
        if max_lag <= min_lag or rms < 0.005:
            pitch = 0.0
        else:
            corr = np.correlate(window, window, mode="full")[len(window) - 1 :]
            corr[:min_lag] = 0.0
            lag = int(np.argmax(corr[: max_lag + 1]))
            pitch = sample_rate / lag if lag else 0.0
        rows.append([pitch / 200.0, rms * 10.0])
    return np.asarray(rows, dtype=np.float32)


def stable_labels(labels: np.ndarray) -> list[str]:
    mapping: dict[int, int] = {}
    result = []
    for label in labels.tolist():
        label = int(label)
        if label not in mapping:
            mapping[label] = len(mapping) + 1
        result.append(f"SPEAKER_{mapping[label]}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-speakers", type=int, default=2)
    args = parser.parse_args()
    started = time.perf_counter()

    boundary_model = WhisperModel("base", device="cpu", compute_type="int8", download_root=str(CACHE_DIR))
    boundaries, boundary_info = boundary_model.transcribe(
        str(args.audio),
        language="th",
        task="transcribe",
        beam_size=5,
        vad_filter=True,
        word_timestamps=True,
        condition_on_previous_text=False,
    )
    boundaries = list(boundaries)

    processor = AutoProcessor.from_pretrained(THAI_MODEL_ID)
    thai_model = AutoModelForSpeechSeq2Seq.from_pretrained(THAI_MODEL_ID, torch_dtype=torch.float32)
    thai_asr = pipeline(
        "automatic-speech-recognition",
        model=thai_model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        device=-1,
        return_timestamps=False,
    )

    full_audio, sample_rate = sf.read(str(args.audio), dtype="float32")
    if full_audio.ndim > 1:
        full_audio = np.mean(full_audio, axis=1)
    temp_dir = args.output.parent / ".segments"
    temp_dir.mkdir(parents=True, exist_ok=True)
    thai_texts = []
    for index, segment in enumerate(boundaries):
        start = max(0, int((segment.start - 0.15) * sample_rate))
        end = min(len(full_audio), int((segment.end + 0.15) * sample_rate))
        temp_path = temp_dir / f"segment_{index:03d}.wav"
        sf.write(str(temp_path), full_audio[start:end], sample_rate, subtype="PCM_16")
        output = thai_asr(
            str(temp_path),
            generate_kwargs={"language": "th", "task": "transcribe"},
        )
        thai_texts.append(" ".join((output.get("text") or "").strip().split()))

    features = pitch_features(args.audio, boundaries)
    if len(features) >= 2 and args.expected_speakers >= 2:
        cluster_ids = LocalWhisperAdapter._kmeans(
            features, min(args.expected_speakers, len(features))
        )
    else:
        cluster_ids = np.zeros(len(features), dtype=int)
    speakers = stable_labels(cluster_ids)

    result = {
        "adapter": {
            "providerId": "local-thai-biodatlab-segmented",
            "asrModel": THAI_MODEL_ID,
            "boundaryModel": "Systran/faster-whisper-base",
            "diarization": "pitch-kmeans-baseline",
            "language": boundary_info.language,
            "sttFee": 0,
        },
        "audio": {"path": str(args.audio), "sizeBytes": args.audio.stat().st_size},
        "processingSeconds": round(time.perf_counter() - started, 3),
        "detectedLanguage": boundary_info.language,
        "segments": [
            {
                "speaker": speakers[index],
                "startMs": int(round(segment.start * 1000)),
                "endMs": int(round(segment.end * 1000)),
                "text": thai_texts[index],
            }
            for index, segment in enumerate(boundaries)
            if thai_texts[index]
        ],
        "rawBoundaryCount": len(boundaries),
        "speakerClusterIds": cluster_ids.tolist(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
