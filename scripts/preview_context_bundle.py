#!/usr/bin/env python3
"""Preview the ordered context bundle for a manifest name or path."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from context_tools import anchor_files, analyze_repo_signals, describe_weight, rank_examples
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
    parser.add_argument(
        "--show-weights",
        action="store_true",
        help="Annotate bundle entries with context weighting metadata.",
    )
    parser.add_argument(
        "--show-anchors",
        action="store_true",
        help="Print the assistant memory anchors that pair well with the bundle.",
    )
    parser.add_argument(
        "--repo",
        help="Optional repo path to compare against repo-signal hints for this manifest.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of plain text.",
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
    task_hints = normalize_string_list(data.get("task_hints"))
    ranked_examples = rank_examples(
        repo_root,
        workflow_names=task_hints,
        stack_names=[str(data.get("primary_stack", "")), *secondary_stacks],
        archetype_names=[str(data.get("archetype", ""))],
        preferred_paths=normalize_string_list(data.get("preferred_examples")),
        limit=5,
    )
    anchors = anchor_files(repo_root)

    repo_signal_summary: dict[str, list[dict[str, object]]] | None = None
    if args.repo:
        repo_signal_summary = analyze_repo_signals(repo_root, Path(args.repo).expanduser().resolve())

    if args.json:
        payload = {
            "manifest": manifest_path.relative_to(repo_root).as_posix(),
            "name": data.get("name", ""),
            "archetype": data.get("archetype", ""),
            "primary_stack": data.get("primary_stack", ""),
            "secondary_stacks": secondary_stacks,
            "bundle": [
                {
                    "path": entry,
                    "weight": describe_weight(repo_root, entry).weight,
                    "tier": describe_weight(repo_root, entry).tier,
                    "reason": describe_weight(repo_root, entry).reason,
                }
                for entry in ordered_bundle
            ],
            "templates": templates,
            "warnings": warnings,
            "anchors": anchors,
            "ranked_examples": ranked_examples,
            "repo_signal_summary": repo_signal_summary,
        }
        print(json.dumps(payload, indent=2))
        return 0

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
        if args.show_weights:
            weight = describe_weight(repo_root, entry)
            print(f"{index}. {entry} [{weight.weight} {weight.tier}]")
            print(f"   reason: {weight.reason}")
        else:
            print(f"{index}. {entry}")

    if ranked_examples:
        print()
        print("Ranked examples:")
        for example in ranked_examples:
            print(
                f"- {example.get('path')} "
                + f"(score={example.get('score')}, "
                + f"level={example.get('verification_level')}, "
                + f"confidence={example.get('confidence')})"
            )

    if args.show_templates and templates:
        print()
        print("Recommended templates:")
        for template in templates:
            print(f"- {template}")

    if args.show_anchors and anchors:
        print()
        print("Assistant memory anchors:")
        for anchor in anchors:
            print(f"- {anchor}")

    if warnings:
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")

    if repo_signal_summary:
        print()
        print("Repo signal comparison:")
        for group_name in ("stacks", "archetypes", "workflows", "manifests"):
            group = repo_signal_summary.get(group_name, [])
            if not group:
                continue
            print(f"- {group_name}:")
            for entry in group[:3]:
                print(
                    "  "
                    + f"{entry.get('name')} (score={entry.get('score')}, matched={', '.join(entry.get('matched_patterns', []))})"
                )

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
