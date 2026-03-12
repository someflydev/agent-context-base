#!/usr/bin/env python3
"""Preview the ordered context bundle for a manifest name or path."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from manifest_tools import build_context_bundle, normalize_string_list, parse_manifest, resolve_manifest


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""

    parser = argparse.ArgumentParser(
        description="Preview the ordered context bundle for a manifest name or path.",
    )
    parser.add_argument("manifest", help="Manifest name like backend-api-fastapi-polars or a path")
    parser.add_argument(
        "--show-templates",
        action="store_true",
        help="Print recommended templates after the main load order.",
    )
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv[1:])
    repo_root = Path(__file__).resolve().parents[1]

    try:
        manifest_path = resolve_manifest(repo_root, args.manifest)
        data = parse_manifest(manifest_path)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    ordered_bundle = build_context_bundle(manifest_path, data, repo_root)
    secondary_stacks = normalize_string_list(data.get("secondary_stacks"))
    warnings = normalize_string_list(data.get("warnings"))
    templates = normalize_string_list(data.get("recommended_templates"))

    print(f"Manifest: {manifest_path.relative_to(repo_root).as_posix()}")
    print(f"Name: {data.get('name', '')}")
    print(f"Description: {data.get('description', '')}")
    print(f"Archetype: {data.get('archetype', '')}")
    print(f"Primary stack: {data.get('primary_stack', '')}")
    if secondary_stacks:
        print(f"Secondary stacks: {', '.join(secondary_stacks)}")
    print(f"Dokku relevance: {data.get('dokku_relevance', '')}")
    print(f"Prompt-first support: {data.get('prompt_first_support', '')}")
    print()
    print("Load order:")
    for index, entry in enumerate(ordered_bundle, start=1):
        print(f"{index}. {entry}")

    if args.show_templates and templates:
        print()
        print("Recommended templates:")
        for template in templates:
            print(f"- {template}")

    if warnings:
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
