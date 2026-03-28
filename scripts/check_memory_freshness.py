#!/usr/bin/env python3
"""Check whether context/MEMORY.md still looks small, current, and operational."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


REQUIRED_SECTIONS = (
    "Current Objective",
    "Active Working Set",
    "Files Already Inspected",
    "Important Findings",
    "Decisions Already Made",
    "Next Steps",
    "Stop Condition",
    "Last Updated",
)

CRITICAL_SECTIONS = (
    "Current Objective",
    "Active Working Set",
    "Next Steps",
    "Stop Condition",
)

PLACEHOLDER_PATTERNS = (
    re.compile(r"<[^>]+>"),
    re.compile(r"\bTODO\b", flags=re.IGNORECASE),
    re.compile(r"\bTBD\b", flags=re.IGNORECASE),
    re.compile(r"\bsame as above\b", flags=re.IGNORECASE),
    re.compile(r"\bfill in\b", flags=re.IGNORECASE),
    re.compile(r"^\s*-\s*$", flags=re.MULTILINE),
)


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""

    parser = argparse.ArgumentParser(
        description="Warn when context/MEMORY.md is missing key sections, stale, or overly large.",
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Repo path to inspect. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--memory-path",
        default="context/MEMORY.md",
        help="Path to inspect relative to the repo root. Defaults to context/MEMORY.md.",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=140,
        help="Warn when context/MEMORY.md exceeds this many lines. Defaults to 140.",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=1500,
        help="Warn when context/MEMORY.md exceeds this many words. Defaults to 1500.",
    )
    parser.add_argument(
        "--max-age-hours",
        type=int,
        default=72,
        help="Warn when the Last Updated timestamp is older than this many hours. Defaults to 72.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 when warnings are found.",
    )
    return parser


def resolve_from_root(root: Path, raw_path: str) -> Path:
    """Resolve a path relative to the repo root unless it is already absolute."""

    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return root / path


def parse_sections(text: str) -> dict[str, str]:
    """Parse markdown level-two sections into a mapping."""

    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def parse_last_updated(section_text: str) -> datetime | None:
    """Parse a basic YYYY-MM-DD HH:MM style timestamp from Last Updated."""

    match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(?::\d{2})?)", section_text)
    if not match:
        return None
    raw_value = match.group(1)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(raw_value, fmt)
        except ValueError:
            continue
    return None


def main(argv: list[str]) -> int:
    """Run the freshness checker."""

    parser = build_parser()
    args = parser.parse_args(argv[1:])
    repo_root = Path(args.repo).expanduser().resolve()
    if not repo_root.exists():
        print(f"Repo path does not exist: {repo_root}", file=sys.stderr)
        return 1

    memory_path = resolve_from_root(repo_root, args.memory_path)
    warnings: list[str] = []
    if not memory_path.exists():
        warnings.append(f"Missing MEMORY file: {memory_path}")
    else:
        text = memory_path.read_text(encoding="utf-8")
        sections = parse_sections(text)

        missing_sections = [section for section in REQUIRED_SECTIONS if section not in sections]
        if missing_sections:
            warnings.append(f"Missing key sections: {', '.join(missing_sections)}")

        for section in CRITICAL_SECTIONS:
            if section in sections and not sections[section].strip():
                warnings.append(f"Section is present but empty: {section}")

        line_count = len(text.splitlines())
        word_count = len(re.findall(r"\S+", text))
        if line_count > args.max_lines:
            warnings.append(
                f"context/MEMORY.md is getting large: {line_count} lines exceeds the {args.max_lines} line guideline"
            )
        if word_count > args.max_words:
            warnings.append(
                f"context/MEMORY.md is getting large: {word_count} words exceeds the {args.max_words} word guideline"
            )

        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(text):
                warnings.append(f"Found placeholder or stale wording pattern: {pattern.pattern}")

        if "Last Updated" in sections:
            timestamp = parse_last_updated(sections["Last Updated"])
            if timestamp is None:
                warnings.append("Could not parse the Last Updated timestamp")
            elif datetime.now() - timestamp > timedelta(hours=args.max_age_hours):
                warnings.append(
                    f"Last Updated looks stale: older than {args.max_age_hours} hours ({timestamp.strftime('%Y-%m-%d %H:%M')})"
                )

    if warnings:
        print("MEMORY freshness warnings:")
        for warning in warnings:
            print(f"- {warning}")
        return 1 if args.strict else 0

    print(f"MEMORY freshness check passed: {memory_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
