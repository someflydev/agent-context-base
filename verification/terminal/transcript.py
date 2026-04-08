from __future__ import annotations

import difflib
import re
from pathlib import Path
from typing import Optional


ANSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
TIMESTAMP_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\b")
JOB_ID_RE = re.compile(r"\bjob-\d+\b")
JSON_DURATION_RE = re.compile(r'("duration_s"\s*:\s*)(-?\d+(?:\.\d+)?)')
PLAIN_DURATION_RE = re.compile(r"(Duration \(s\):\s*)(-?\d+(?:\.\d+)?)")


def normalize_transcript(text: str) -> str:
    normalized = ANSI_RE.sub("", text)
    normalized = TIMESTAMP_RE.sub("<TIMESTAMP>", normalized)
    normalized = JOB_ID_RE.sub("<JOB_ID>", normalized)
    normalized = JSON_DURATION_RE.sub(r"\1<DURATION>", normalized)
    normalized = PLAIN_DURATION_RE.sub(r"\1<DURATION>", normalized)

    lines = [re.sub(r"[ \t]+", " ", line).rstrip() for line in normalized.splitlines()]
    normalized = "\n".join(lines).strip()
    if normalized:
        normalized += "\n"
    return normalized


def diff_transcripts(expected: str, actual: str) -> str:
    expected_normalized = normalize_transcript(expected).splitlines(keepends=True)
    actual_normalized = normalize_transcript(actual).splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            expected_normalized,
            actual_normalized,
            fromfile="expected",
            tofile="actual",
        )
    )


def save_golden(name: str, content: str, golden_dir: Path) -> None:
    golden_dir.mkdir(parents=True, exist_ok=True)
    (golden_dir / f"{name}.golden.txt").write_text(normalize_transcript(content), encoding="utf-8")


def load_golden(name: str, golden_dir: Path) -> Optional[str]:
    path = golden_dir / f"{name}.golden.txt"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def assert_transcript(name: str, actual: str, golden_dir: Path, update: bool = False) -> bool:
    normalized_actual = normalize_transcript(actual)
    golden = load_golden(name, golden_dir)
    if update or golden is None:
        save_golden(name, normalized_actual, golden_dir)
        return True

    normalized_expected = normalize_transcript(golden)
    if normalized_expected == normalized_actual:
        return True

    print(diff_transcripts(normalized_expected, normalized_actual))
    return False
