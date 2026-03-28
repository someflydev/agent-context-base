#!/usr/bin/env python3
"""Initialize a repo-local context/MEMORY.md from the starter template."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


FALLBACK_TEMPLATE = """# MEMORY.md

## Current Objective
- 

## Current Context
- Active stack:
- Active archetype:
- Active manifest or profile:
- Prompt batch or deployment posture:

## Active Working Set
- 

## Files Already Inspected
- 

## Important Findings
- 

## Decisions Already Made
- Decision:
  Reason:

## Explicitly Not Doing
- 

## Blockers Or Risks
- 

## Next Steps
- 
- 

## Stop Condition
- 

## Last Updated
- YYYY-MM-DD HH:MM local time -
"""


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""

    parser = argparse.ArgumentParser(
        description="Create a repo-local context/MEMORY.md from the starter template if it is missing.",
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Repo path to initialize. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--memory-path",
        default="context/MEMORY.md",
        help="Path to write relative to the repo root. Defaults to context/MEMORY.md.",
    )
    parser.add_argument(
        "--template",
        help="Optional template path. Relative paths are resolved from the repo root first.",
    )
    parser.add_argument(
        "--with-handoffs",
        action="store_true",
        help="Create the handoff directory as well.",
    )
    parser.add_argument(
        "--handoff-dir",
        default="artifacts/handoffs",
        help="Handoff directory to create when --with-handoffs is used.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing context/MEMORY.md.",
    )
    return parser


def resolve_from_root(root: Path, raw_path: str) -> Path:
    """Resolve a path relative to the repo root unless it is already absolute."""

    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return root / path


def load_template(repo_root: Path, explicit_template: str | None) -> tuple[str, str]:
    """Return the template text and the source label."""

    script_root = Path(__file__).resolve().parents[1]
    candidates: list[Path] = []
    if explicit_template:
        candidates.append(resolve_from_root(repo_root, explicit_template))
    candidates.extend(
        [
            repo_root / "templates/memory/MEMORY.template.md",
            script_root / "templates/memory/MEMORY.template.md",
            repo_root / "context/memory/MEMORY.template.md",
            script_root / "context/memory/MEMORY.template.md",
        ]
    )

    seen: set[Path] = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.exists():
            return candidate.read_text(encoding="utf-8"), candidate.as_posix()

    return FALLBACK_TEMPLATE, "embedded fallback"


def ensure_directory(path: Path) -> None:
    """Create the target directory if needed."""

    path.parent.mkdir(parents=True, exist_ok=True)


def main(argv: list[str]) -> int:
    """Run the initializer."""

    parser = build_parser()
    args = parser.parse_args(argv[1:])
    repo_root = Path(args.repo).expanduser().resolve()
    if not repo_root.exists():
        print(f"Repo path does not exist: {repo_root}", file=sys.stderr)
        return 1

    memory_path = resolve_from_root(repo_root, args.memory_path)
    template_text, template_source = load_template(repo_root, args.template)

    actions: list[str] = []
    memory_existed = memory_path.exists()
    if memory_existed and not args.force:
        actions.append(f"Left existing file unchanged: {memory_path}")
    else:
        ensure_directory(memory_path)
        memory_path.write_text(template_text.rstrip() + "\n", encoding="utf-8")
        verb = "Overwrote" if memory_existed else "Created"
        actions.append(f"{verb} {memory_path} from {template_source}")

    if args.with_handoffs:
        handoff_dir = resolve_from_root(repo_root, args.handoff_dir)
        handoff_dir.mkdir(parents=True, exist_ok=True)
        actions.append(f"Ensured handoff directory exists: {handoff_dir}")

    for action in actions:
        print(action)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
