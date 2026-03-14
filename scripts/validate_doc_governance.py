#!/usr/bin/env python3
"""Validate documentation freshness guardrails for this repository."""

from __future__ import annotations

import sys
from pathlib import Path

from context_tools import validate_markdown_cross_references, validate_mermaid_reference_hints


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    errors = [
        *validate_markdown_cross_references(repo_root),
        *validate_mermaid_reference_hints(repo_root),
    ]
    if errors:
        print("Documentation governance validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Validated markdown links and obvious Mermaid path references.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
