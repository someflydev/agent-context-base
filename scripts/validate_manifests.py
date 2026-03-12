#!/usr/bin/env python3
"""Validate the v2 manifest files for schema and reference correctness."""

from __future__ import annotations

import sys
from pathlib import Path

from manifest_tools import validate_manifest


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    manifest_dir = repo_root / "manifests"
    manifest_paths = sorted(manifest_dir.glob("*.yaml"))

    if not manifest_paths:
        print("No manifest files found under manifests/.", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for manifest_path in manifest_paths:
        all_errors.extend(validate_manifest(repo_root, manifest_path))

    if all_errors:
        print("Manifest validation failed:", file=sys.stderr)
        for error in all_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(manifest_paths)} manifest files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

