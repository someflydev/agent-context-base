#!/usr/bin/env python3
"""Inspect a generated repo-local `.acb/` payload."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect the `.acb/` payload in a generated repo.")
    parser.add_argument("repo", nargs="?", default=".", help="Repo root containing `.acb/`.")
    parser.add_argument("--json", action="store_true", help="Print the parsed index as JSON.")
    return parser


def load_index(repo_root: Path) -> dict[str, object]:
    index_path = repo_root / ".acb" / "INDEX.json"
    if not index_path.exists():
        raise SystemExit(f"Missing {index_path}")
    return json.loads(index_path.read_text(encoding="utf-8"))


def main() -> int:
    args = build_parser().parse_args()
    repo_root = Path(args.repo).resolve()
    index = load_index(repo_root)
    if args.json:
        print(json.dumps(index, indent=2))
        return 0

    selection = index["selection"]
    print("ACB payload summary")
    print(f"- repo: {repo_root}")
    print(f"- archetype: {selection['archetype']}")
    print(f"- primary stack: {selection['primary_stack']}")
    print(
        "- capabilities: "
        + (", ".join(selection["capabilities"]) if selection["capabilities"] else "none")
    )
    print(
        "- manifests: "
        + (", ".join(selection["selected_manifests"]) if selection["selected_manifests"] else "none")
    )
    print("")
    print("Canonical source modules")
    for layer, modules in index["source_modules"].items():
        print(f"- {layer}:")
        for module in modules:
            metadata = module["metadata"]
            extras = []
            for key in ("acb_archetypes", "acb_stacks", "acb_doctrines", "acb_capabilities", "acb_routers"):
                values = metadata.get(key, [])
                if values:
                    extras.append(f"{key}={','.join(values)}")
            suffix = f" ({'; '.join(extras)})" if extras else ""
            print(f"  - {module['source']} -> {module['target']}{suffix}")
    print("")
    print("Validation coverage")
    coverage_path = repo_root / ".acb" / "validation" / "COVERAGE.json"
    if coverage_path.exists():
        coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
        summary = coverage["summary"]
        print(
            f"- dimensions covered: {summary['covered_validation_dimensions']}/{summary['required_validation_dimensions']}"
        )
        missing = summary["missing_validation_dimensions"]
        print("- missing dimensions: " + (", ".join(missing) if missing else "none"))
    else:
        print("- coverage summary missing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
