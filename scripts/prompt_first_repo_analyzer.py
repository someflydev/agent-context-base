#!/usr/bin/env python3
"""Infer likely stacks, archetypes, workflows, and manifests from repo signals."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from context_tools import analyze_repo_signals, rank_examples


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""

    parser = argparse.ArgumentParser(
        description="Infer likely stacks, archetypes, workflows, and manifests from repo signals.",
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Repo path to analyze. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of plain text.",
    )
    return parser


def main(argv: list[str]) -> int:
    """Run the repo analyzer."""

    parser = build_parser()
    args = parser.parse_args(argv[1:])
    repo_root = Path(__file__).resolve().parents[1]
    target_root = Path(args.repo).expanduser().resolve()
    if not target_root.exists():
        print(f"Repo path does not exist: {target_root}", file=sys.stderr)
        return 1

    signals = analyze_repo_signals(repo_root, target_root)
    top_stack = signals["stacks"][0]["name"] if signals["stacks"] else ""
    top_archetype = signals["archetypes"][0]["name"] if signals["archetypes"] else ""
    top_workflows = [str(entry["name"]) for entry in signals["workflows"][:3]]
    ranked_examples = rank_examples(
        repo_root,
        workflow_names=top_workflows,
        stack_names=[top_stack] if top_stack else [],
        archetype_names=[top_archetype] if top_archetype else [],
        limit=5,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "repo": target_root.as_posix(),
                    "signals": signals,
                    "ranked_examples": ranked_examples,
                },
                indent=2,
            )
        )
        return 0

    print(f"Repo: {target_root}")
    for group_name in ("stacks", "archetypes", "workflows", "manifests"):
        group = signals[group_name]
        if not group:
            continue
        print()
        print(f"{group_name.title()}:")
        for entry in group[:5]:
            print(
                f"- {entry['name']} (score={entry['score']}, matched={', '.join(entry['matched_patterns'])})"
            )
            guidance = str(entry.get("guidance", "")).strip()
            if guidance:
                print(f"  guidance: {guidance}")

    if ranked_examples:
        print()
        print("Suggested canonical examples:")
        for example in ranked_examples:
            print(f"- {example.get('path')} (score={example.get('score')})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
