#!/usr/bin/env python3
"""Local, zero-STT-fee Speech-to-Text adapter spike.

The ASR model is faster-whisper. Speaker labels are a deliberately small
baseline for this spike: it clusters acoustic features extracted from each
ASR segment. It is useful for an end-to-end contract test, but it is not a
replacement for a trained diarization pipeline on real meetings.
"""

from __future__ import annotations

import argparse
import json
import math
import time
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from faster_whisper import WhisperModel


@dataclass
class NormalizedSegment:
    speaker: str
    startMs: int
    endMs: int
    text: str


class LocalWhisperAdapter:
    """Provider-neutral batch adapter backed by a local Whisper model."""

    def __init__(
        self,
        model_size: str = "base",
        cache_dir: str | Path = "tools/free_stt_spike/cache",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self.provider_id = "local-faster-whisper"
        self.model_size = model_size
        self.cache_dir = Path(cache_dir)
        self.device = device
        self.compute_type = compute_type
        self._model: WhisperModel | None = None

    def capabilities(self) -> dict[str, Any]:
        return {
            "batch": True,
            "live": False,
            "diarization": "baseline-acoustic-clustering",
            "wordTimestamps": True,
            "languageCode": "th",
            "sttFee": 0,
        }

    def _load_model(self) -> WhisperModel:
        if self._model is None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=str(self.cache_dir),
            )
        return self._model

    @staticmethod
    def _read_mono_wav(path: Path) -> tuple[np.ndarray, int]:
        with wave.open(str(path), "rb") as handle:
            sample_rate = handle.getframerate()
            channels = handle.getnchannels()
            sample_width = handle.getsampwidth()
            frames = handle.readframes(handle.getnframes())
        if sample_width != 2:
            raise ValueError("spike currently expects 16-bit PCM WAV")
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        if channels > 1:
            audio = audio.reshape(-1, channels).mean(axis=1)
        return audio, sample_rate

    @staticmethod
    def _pitch_hz(samples: np.ndarray, sample_rate: int) -> float:
        """Estimate the strongest periodic pitch for a segment.

        This is intentionally simple and deterministic. It is sufficient for
        the synthetic smoke fixture, while real meeting audio must use a real
        diarization model and benchmarked thresholds.
        """
        if len(samples) < sample_rate // 10:
            return 0.0
        samples = samples - float(np.mean(samples))
        rms = float(np.sqrt(np.mean(samples * samples)))
        if rms < 0.005:
            return 0.0
        min_lag = max(1, int(sample_rate / 350))
        max_lag = min(len(samples) - 1, int(sample_rate / 70))
        if max_lag <= min_lag:
            return 0.0
        correlation = np.correlate(samples, samples, mode="full")[len(samples) - 1 :]
        correlation[:min_lag] = 0.0
        lag = int(np.argmax(correlation[: max_lag + 1]))
        return float(sample_rate / lag) if lag > 0 else 0.0

    @classmethod
    def _features_for_segments(
        cls, path: Path, segments: list[Any]
    ) -> np.ndarray:
        audio, sample_rate = cls._read_mono_wav(path)
        feature_rows: list[list[float]] = []
        for segment in segments:
            start = max(0, int(segment.start * sample_rate))
            end = min(len(audio), max(start + 1, int(segment.end * sample_rate)))
            window = audio[start:end]
            rms = float(np.sqrt(np.mean(window * window))) if len(window) else 0.0
            pitch = cls._pitch_hz(window, sample_rate)
            # Pitch is the useful signal for the synthetic fixture; RMS adds a
            # second dimension so the clustering is not a hard-coded label map.
            feature_rows.append([pitch / 200.0, rms * 10.0])
        return np.asarray(feature_rows, dtype=np.float32)

    @staticmethod
    def _kmeans(features: np.ndarray, k: int, iterations: int = 30) -> np.ndarray:
        if len(features) == 0:
            return np.asarray([], dtype=np.int64)
        k = max(1, min(k, len(features)))
        if k == 1:
            return np.zeros(len(features), dtype=np.int64)
        # Deterministic farthest-point initialization.
        centers = [features[0]]
        while len(centers) < k:
            distances = np.min(
                np.stack([np.sum((features - center) ** 2, axis=1) for center in centers]),
                axis=0,
            )
            centers.append(features[int(np.argmax(distances))])
        centers_array = np.asarray(centers, dtype=np.float32)
        labels = np.zeros(len(features), dtype=np.int64)
        for _ in range(iterations):
            distances = np.stack(
                [np.sum((features - center) ** 2, axis=1) for center in centers_array]
            )
            next_labels = np.argmin(distances, axis=0)
            if np.array_equal(labels, next_labels):
                break
            labels = next_labels
            for index in range(k):
                members = features[labels == index]
                if len(members):
                    centers_array[index] = np.mean(members, axis=0)
        return labels

    @staticmethod
    def _stable_speaker_names(labels: np.ndarray) -> list[str]:
        # Provider diarization labels are remapped by first appearance within
        # one meeting. They never identify a person across meetings.
        mapping: dict[int, int] = {}
        next_id = 1
        result: list[str] = []
        for label in labels.tolist():
            if int(label) not in mapping:
                mapping[int(label)] = next_id
                next_id += 1
            result.append(f"SPEAKER_{mapping[int(label)]}")
        return result

    def transcribe_batch(
        self,
        audio_path: str | Path,
        language: str = "th",
        expected_speakers: int = 2,
        no_speech_threshold: float = 0.6,
    ) -> dict[str, Any]:
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(path)
        if language not in {"th", "th-TH"}:
            raise ValueError("this spike is intentionally limited to Thai")
        model = self._load_model()
        started = time.perf_counter()
        raw_segments, info = model.transcribe(
            str(path),
            language="th",
            task="transcribe",
            beam_size=5,
            vad_filter=True,
            word_timestamps=True,
            condition_on_previous_text=False,
            no_speech_threshold=no_speech_threshold,
        )
        raw_segments = list(raw_segments)
        features = self._features_for_segments(path, raw_segments)
        labels = self._kmeans(features, expected_speakers)
        speaker_names = self._stable_speaker_names(labels)
        normalized = [
            NormalizedSegment(
                speaker=speaker_names[index],
                startMs=max(0, int(round(segment.start * 1000))),
                endMs=max(0, int(round(segment.end * 1000))),
                text=" ".join(segment.text.strip().split()),
            )
            for index, segment in enumerate(raw_segments)
            if segment.text.strip()
        ]
        elapsed = time.perf_counter() - started
        duration_seconds = 0.0
        if raw_segments:
            duration_seconds = max(float(segment.end) for segment in raw_segments)
        return {
            "adapter": {
                "providerId": self.provider_id,
                "model": self.model_size,
                "capabilities": self.capabilities(),
            },
            "audio": {
                "path": str(path),
                "durationMs": int(round(duration_seconds * 1000)),
                "sizeBytes": path.stat().st_size,
            },
            "detectedLanguage": info.language,
            "languageProbability": float(info.language_probability),
            "processingSeconds": round(elapsed, 3),
            "speakerDiagnostics": [
                {
                    "segmentIndex": index,
                    "pitchHz": round(float(features[index][0] * 200.0), 2),
                    "rms": round(float(features[index][1] / 10.0), 5),
                    "cluster": int(labels[index]),
                }
                for index in range(len(raw_segments))
            ],
            "segments": [asdict(segment) for segment in normalized],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="base")
    parser.add_argument("--compute-type", default="int8")
    parser.add_argument("--expected-speakers", type=int, default=2)
    parser.add_argument("--no-speech-threshold", type=float, default=0.6)
    parser.add_argument("--cache-dir", type=Path, default=Path("tools/free_stt_spike/cache"))
    args = parser.parse_args()
    result = LocalWhisperAdapter(
        model_size=args.model,
        cache_dir=args.cache_dir,
        compute_type=args.compute_type,
    ).transcribe_batch(
        args.audio,
        expected_speakers=args.expected_speakers,
        no_speech_threshold=args.no_speech_threshold,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
