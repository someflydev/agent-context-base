#!/usr/bin/env python3
"""Show a practical diff between two files or two directory trees."""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""

    parser = argparse.ArgumentParser(
        description="Show a practical diff between two files or two directory trees.",
    )
    parser.add_argument("left", help="Left file or directory")
    parser.add_argument("right", help="Right file or directory")
    parser.add_argument(
        "--context",
        type=int,
        default=3,
        help="Unified diff context lines. Defaults to 3.",
    )
    parser.add_argument(
        "--ignore-empty-lines",
        action="store_true",
        help="Drop empty lines before diffing text content.",
    )
    return parser


def read_lines(path: Path, ignore_empty_lines: bool) -> list[str]:
    """Return normalized text lines for a file."""

    lines = path.read_text(encoding="utf-8").splitlines()
    if ignore_empty_lines:
        lines = [line for line in lines if line.strip()]
    return [line + "\n" for line in lines]


def diff_files(left: Path, right: Path, context: int, ignore_empty_lines: bool) -> list[str]:
    """Return a unified diff for two text files."""

    return list(
        difflib.unified_diff(
            read_lines(left, ignore_empty_lines),
            read_lines(right, ignore_empty_lines),
            fromfile=left.as_posix(),
            tofile=right.as_posix(),
            n=context,
        )
    )


def diff_directories(left: Path, right: Path, context: int, ignore_empty_lines: bool) -> list[str]:
    """Return a summary diff for two directory trees."""

    output: list[str] = []
    left_files = {
        path.relative_to(left).as_posix(): path
        for path in left.rglob("*")
        if path.is_file()
    }
    right_files = {
        path.relative_to(right).as_posix(): path
        for path in right.rglob("*")
        if path.is_file()
    }

    for relative_path in sorted(left_files.keys() - right_files.keys()):
        output.append(f"Only in {left.as_posix()}: {relative_path}\n")
    for relative_path in sorted(right_files.keys() - left_files.keys()):
        output.append(f"Only in {right.as_posix()}: {relative_path}\n")
    for relative_path in sorted(left_files.keys() & right_files.keys()):
        output.extend(diff_files(left_files[relative_path], right_files[relative_path], context, ignore_empty_lines))
    return output


def main(argv: list[str]) -> int:
    """Run the pattern diff CLI."""

    parser = build_parser()
    args = parser.parse_args(argv[1:])
    left = Path(args.left).expanduser().resolve()
    right = Path(args.right).expanduser().resolve()

    if not left.exists():
        print(f"Left path does not exist: {left}", file=sys.stderr)
        return 1
    if not right.exists():
        print(f"Right path does not exist: {right}", file=sys.stderr)
        return 1

    if left.is_dir() != right.is_dir():
        print("Both paths must be files or both paths must be directories.", file=sys.stderr)
        return 1

    if left.is_file():
        diff_lines = diff_files(left, right, args.context, args.ignore_empty_lines)
    else:
        diff_lines = diff_directories(left, right, args.context, args.ignore_empty_lines)

    if not diff_lines:
        print("No differences found.")
        return 0

    sys.stdout.writelines(diff_lines)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
