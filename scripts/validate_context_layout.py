#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


REQUIRED_PATHS = [
    "AGENT.md",
    "CLAUDE.md",
    "README.md",
    "docs/agent-context-architecture.md",
    "context/doctrine",
    "context/skills",
    "context/workflows",
    "context/stacks",
    "context/archetypes",
    "context/router",
    "manifests/repo.profile.yaml",
    "examples/canonical",
    "templates/base",
    "smoke-tests",
]


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    missing = [path for path in REQUIRED_PATHS if not (root / path).exists()]
    if missing:
        print("Missing required paths:")
        for path in missing:
            print(f"- {path}")
        return 1
    print("Context layout looks complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
