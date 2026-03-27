#!/usr/bin/env python3
"""Verify `.acb/` payload integrity, drift visibility, and coverage gaps."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify `.acb/` payload hashes and report canonical drift or coverage gaps."
    )
    parser.add_argument("repo", nargs="?", default=".", help="Repo root containing `.acb/`.")
    parser.add_argument(
        "--canonical-root",
        help="Optional path to the canonical agent-context-base repo for upstream drift comparison.",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any drift or coverage gap.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable results.")
    return parser


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise SystemExit(f"Missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def maybe_canonical_root(explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit).resolve()
    script_root = Path(__file__).resolve().parents[1]
    if (script_root / "context" / "specs").exists() and (script_root / "context" / "validation").exists():
        return script_root
    return None


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo).resolve()
    index = load_json(repo_root / ".acb" / "INDEX.json")
    coverage = load_json(repo_root / ".acb" / "validation" / "COVERAGE.json")

    local_drift: list[dict[str, str]] = []
    for relative_path, expected_hash in index.get("generated_file_hashes", {}).items():
        full_path = repo_root / relative_path
        if not full_path.exists():
            local_drift.append({"path": relative_path, "reason": "missing"})
            continue
        actual_hash = sha256_path(full_path)
        if actual_hash != expected_hash:
            local_drift.append({"path": relative_path, "reason": "hash-mismatch"})

    canonical_root = maybe_canonical_root(args.canonical_root)
    canonical_drift: list[dict[str, str]] = []
    if canonical_root is not None:
        for modules in index.get("source_modules", {}).values():
            for module in modules:
                source_path = canonical_root / module["source"]
                if not source_path.exists():
                    canonical_drift.append({"path": module["source"], "reason": "canonical-source-missing"})
                    continue
                actual_hash = sha256_path(source_path)
                if actual_hash != module["sha256"]:
                    canonical_drift.append({"path": module["source"], "reason": "canonical-hash-mismatch"})

    summary = coverage["summary"]
    coverage_gaps = list(summary["missing_validation_dimensions"])
    result = {
        "repo": repo_root.as_posix(),
        "canonical_root": canonical_root.as_posix() if canonical_root is not None else None,
        "local_payload_drift": local_drift,
        "canonical_source_drift": canonical_drift,
        "coverage_gaps": coverage_gaps,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("ACB verify")
        print(f"- repo: {repo_root}")
        print(f"- canonical root: {canonical_root if canonical_root is not None else 'unavailable'}")
        print("- local payload drift: " + (str(len(local_drift)) if local_drift else "none"))
        for item in local_drift:
            print(f"  - {item['path']}: {item['reason']}")
        print("- canonical source drift: " + (str(len(canonical_drift)) if canonical_drift else "none"))
        for item in canonical_drift:
            print(f"  - {item['path']}: {item['reason']}")
        print("- coverage gaps: " + (", ".join(coverage_gaps) if coverage_gaps else "none"))

    if args.strict and (local_drift or canonical_drift or coverage_gaps):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
