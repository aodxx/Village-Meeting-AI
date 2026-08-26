#!/usr/bin/env python3
"""Validate a local STT adapter result against a synthetic fixture manifest."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def thai_text(text: str) -> str:
    # For a smoke proxy, compare Thai letters/numbers only and ignore spaces,
    # punctuation, and model formatting differences.
    return "".join(re.findall(r"[ก-๙A-Za-z0-9]", text)).lower()


def edit_distance(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (left_char != right_char),
                )
            )
        previous = current
    return previous[-1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("result", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = json.loads(args.result.read_text(encoding="utf-8"))
    segments = result.get("segments", [])
    expected_texts = manifest.get("expectedTexts", [])
    failures = []

    if result.get("adapter", {}).get("sttFee") != 0:
        failures.append("sttFee is not zero")
    if result.get("detectedLanguage") != "th":
        failures.append("detectedLanguage is not th")
    if len(segments) != len(expected_texts):
        failures.append(f"segment count {len(segments)} != expected {len(expected_texts)}")
    for index, segment in enumerate(segments):
        required = {"speaker", "startMs", "endMs", "text"}
        if not required.issubset(segment):
            failures.append(f"segment {index} misses normalized fields")
        if segment.get("startMs", -1) < 0 or segment.get("endMs", 0) <= segment.get("startMs", 0):
            failures.append(f"segment {index} has invalid timestamp")
        if not segment.get("text", "").strip():
            failures.append(f"segment {index} has empty text")

    normalized_valid = len(segments) == len(expected_texts) and all(
        {"speaker", "startMs", "endMs", "text"}.issubset(segment)
        and segment.get("startMs", -1) >= 0
        and segment.get("endMs", 0) > segment.get("startMs", 0)
        and bool(segment.get("text", "").strip())
        for segment in segments
    )

    observed_labels = [segment.get("speaker") for segment in segments]
    observed_pattern = []
    mapping = {}
    for label in observed_labels:
        if label not in mapping:
            mapping[label] = len(mapping) + 1
        observed_pattern.append(mapping[label])
    expected_pattern = [1 if value == "SPEAKER_A" else 2 for value in manifest.get("expectedOrder", [])]
    if observed_pattern != expected_pattern:
        failures.append(f"speaker order {observed_pattern} != expected {expected_pattern}")

    comparisons = []
    for expected, segment in zip(expected_texts, segments):
        expected_clean = thai_text(expected)
        actual_clean = thai_text(segment.get("text", ""))
        distance = edit_distance(expected_clean, actual_clean)
        comparisons.append(
            {
                "expectedLength": len(expected_clean),
                "actualLength": len(actual_clean),
                "charErrors": distance,
                "cer": round(distance / max(1, len(expected_clean)), 4),
            }
        )
    average_cer = round(sum(item["cer"] for item in comparisons) / max(1, len(comparisons)), 4)
    output = {
        "passed": not failures,
        "failures": failures,
        "checks": {
            "zeroSttFee": result.get("adapter", {}).get("sttFee") == 0,
            "thaiDetected": result.get("detectedLanguage") == "th",
            "normalizedSegments": normalized_valid,
            "speakerOrder": observed_pattern == expected_pattern,
            "averageCerProxy": average_cer,
        },
        "segmentComparisons": comparisons,
        "resultMetadata": {
            "adapter": result.get("adapter"),
            "processingSeconds": result.get("processingSeconds"),
            "segmentCount": len(segments),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    raise SystemExit(0 if output["passed"] else 1)


if __name__ == "__main__":
    main()
