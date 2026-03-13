#!/usr/bin/env python3
"""Create a timestamped handoff snapshot with optional carry-forward from MEMORY.md."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


FALLBACK_TEMPLATE = """# Handoff Snapshot - <title>

- Timestamp: YYYY-MM-DD HH:MM local time
- Repo shape:
- Active manifest or profile:
- Completed prompt or milestone:
- Next intended prompt or phase:

## Objective

<current task objective>

## State At Handoff

- 

## Completed Work

- 

## Remaining Work

- 

## Decisions Already Made

- 

## Explicitly Not Doing

- 

## Blockers Or Risks

- 

## Exact Files To Inspect Next

- path/to/file

## Validation Status

- 
"""


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""

    parser = argparse.ArgumentParser(
        description="Create a timestamped handoff snapshot from the starter template.",
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Repo path to use. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--title",
        default="handoff",
        help="Short handoff title used in the heading and filename slug.",
    )
    parser.add_argument(
        "--slug",
        help="Optional explicit filename slug. Defaults to a slugified title.",
    )
    parser.add_argument(
        "--handoff-dir",
        default="artifacts/handoffs",
        help="Directory for handoff snapshots relative to the repo root.",
    )
    parser.add_argument(
        "--template",
        help="Optional handoff template path. Relative paths are resolved from the repo root first.",
    )
    parser.add_argument(
        "--memory-path",
        default="MEMORY.md",
        help="Path to MEMORY.md relative to the repo root.",
    )
    parser.add_argument(
        "--from-memory",
        action="store_true",
        help="Carry forward relevant sections from the current MEMORY.md when present.",
    )
    parser.add_argument(
        "--timestamp",
        help="Override the timestamp used in the filename and header. Format: YYYY-MM-DD-HHMMSS.",
    )
    parser.add_argument(
        "--repo-shape",
        default="",
        help="Optional repo shape or archetype label.",
    )
    parser.add_argument(
        "--manifest",
        default="",
        help="Optional active manifest or profile label.",
    )
    parser.add_argument(
        "--completed-milestone",
        default="",
        help="Optional completed prompt, milestone, or checkpoint label.",
    )
    parser.add_argument(
        "--next-phase",
        default="",
        help="Optional next intended prompt or phase label.",
    )
    parser.add_argument(
        "--objective",
        default="",
        help="Optional objective override.",
    )
    parser.add_argument(
        "--state",
        action="append",
        default=[],
        help="Add a bullet under 'State At Handoff'. May be repeated.",
    )
    parser.add_argument(
        "--completed",
        action="append",
        default=[],
        help="Add a bullet under 'Completed Work'. May be repeated.",
    )
    parser.add_argument(
        "--remaining",
        action="append",
        default=[],
        help="Add a bullet under 'Remaining Work'. May be repeated.",
    )
    parser.add_argument(
        "--decision",
        action="append",
        default=[],
        help="Add a bullet under 'Decisions Already Made'. May be repeated.",
    )
    parser.add_argument(
        "--not-doing",
        action="append",
        default=[],
        help="Add a bullet under 'Explicitly Not Doing'. May be repeated.",
    )
    parser.add_argument(
        "--risk",
        action="append",
        default=[],
        help="Add a bullet under 'Blockers Or Risks'. May be repeated.",
    )
    parser.add_argument(
        "--next-file",
        action="append",
        default=[],
        help="Add a bullet under 'Exact Files To Inspect Next'. May be repeated.",
    )
    parser.add_argument(
        "--validation",
        action="append",
        default=[],
        help="Add a bullet under 'Validation Status'. May be repeated.",
    )
    return parser


def resolve_from_root(root: Path, raw_path: str) -> Path:
    """Resolve a path relative to the repo root unless it is already absolute."""

    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return root / path


def load_template(repo_root: Path, explicit_template: str | None) -> str:
    """Return the template text."""

    script_root = Path(__file__).resolve().parents[1]
    candidates: list[Path] = []
    if explicit_template:
        candidates.append(resolve_from_root(repo_root, explicit_template))
    candidates.extend(
        [
            repo_root / "templates/memory/HANDOFF-SNAPSHOT.template.md",
            script_root / "templates/memory/HANDOFF-SNAPSHOT.template.md",
        ]
    )

    seen: set[Path] = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")

    return FALLBACK_TEMPLATE


def slugify(text: str) -> str:
    """Convert arbitrary text into a filesystem-friendly slug."""

    lowered = text.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "handoff"


def parse_sections(text: str) -> dict[str, str]:
    """Parse markdown level-two sections into a mapping."""

    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def combine_blocks(*blocks: str) -> str:
    """Join non-empty markdown blocks with a blank line."""

    cleaned = [block.strip() for block in blocks if block.strip()]
    return "\n\n".join(cleaned)


def format_bullets(values: list[str], fallback: str = "- ") -> str:
    """Format a list of values as markdown bullets."""

    cleaned = [value.strip() for value in values if value.strip()]
    if not cleaned:
        return fallback
    return "\n".join(f"- {value}" for value in cleaned)


def replace_line(text: str, prefix: str, value: str) -> str:
    """Replace the first metadata line with the supplied value."""

    pattern = re.compile(rf"^- {re.escape(prefix)}:.*$", flags=re.MULTILINE)
    return pattern.sub(f"- {prefix}: {value}", text, count=1)


def replace_section(text: str, heading: str, body: str) -> str:
    """Replace the body of a level-two markdown section."""

    pattern = re.compile(rf"(## {re.escape(heading)}\n\n)(.*?)(?=\n## |\Z)", flags=re.DOTALL)
    return pattern.sub(lambda match: f"{match.group(1)}{body.rstrip()}\n", text, count=1)


def extract_context_value(context_block: str, label: str) -> str:
    """Return the value after a labeled bullet inside the Current Context section."""

    for line in context_block.splitlines():
        if line.startswith(f"- {label}:"):
            return line.split(":", 1)[1].strip().strip("`")
    return ""


def build_timestamp(raw_timestamp: str | None) -> tuple[str, str]:
    """Return the filename timestamp and display timestamp."""

    try:
        timestamp = datetime.strptime(raw_timestamp, "%Y-%m-%d-%H%M%S") if raw_timestamp else datetime.now()
    except ValueError as exc:
        raise ValueError("timestamp must use YYYY-MM-DD-HHMMSS") from exc
    return timestamp.strftime("%Y-%m-%d-%H%M%S"), timestamp.strftime("%Y-%m-%d %H:%M local time")


def main(argv: list[str]) -> int:
    """Run the handoff snapshot generator."""

    parser = build_parser()
    args = parser.parse_args(argv[1:])
    repo_root = Path(args.repo).expanduser().resolve()
    if not repo_root.exists():
        print(f"Repo path does not exist: {repo_root}", file=sys.stderr)
        return 1

    template_text = load_template(repo_root, args.template)
    slug = args.slug or slugify(args.title)
    try:
        filename_timestamp, display_timestamp = build_timestamp(args.timestamp)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    handoff_dir = resolve_from_root(repo_root, args.handoff_dir)
    handoff_dir.mkdir(parents=True, exist_ok=True)

    memory_sections: dict[str, str] = {}
    if args.from_memory:
        memory_path = resolve_from_root(repo_root, args.memory_path)
        if memory_path.exists():
            memory_sections = parse_sections(memory_path.read_text(encoding="utf-8"))

    current_context = memory_sections.get("Current Context", "")
    current_objective = memory_sections.get("Current Objective", "")
    active_working_set = memory_sections.get("Active Working Set", "")
    important_findings = memory_sections.get("Important Findings", "")
    decisions = memory_sections.get("Decisions Already Made", "")
    explicitly_not_doing = memory_sections.get("Explicitly Not Doing", "")
    blockers = memory_sections.get("Blockers Or Risks", "")
    next_steps = memory_sections.get("Next Steps", "")
    last_updated = memory_sections.get("Last Updated", "")
    normalized_last_updated = last_updated.removeprefix("- ").strip()

    repo_shape = args.repo_shape or extract_context_value(current_context, "Active archetype")
    manifest = args.manifest or extract_context_value(current_context, "Active manifest or profile")
    if not manifest:
        manifest = extract_context_value(current_context, "Active manifest")
    objective = args.objective or current_objective or "<current task objective>"

    state_block = format_bullets(args.state) if args.state else combine_blocks(current_context, important_findings) or "- "
    completed_block = format_bullets(args.completed)
    remaining_block = format_bullets(args.remaining) if args.remaining else (next_steps or "- ")
    decision_block = format_bullets(args.decision) if args.decision else (decisions or "- ")
    not_doing_block = format_bullets(args.not_doing) if args.not_doing else (explicitly_not_doing or "- ")
    risk_block = format_bullets(args.risk) if args.risk else (blockers or "- ")
    next_files_block = format_bullets(args.next_file) if args.next_file else (active_working_set or "- path/to/file")
    if args.validation:
        validation_block = format_bullets(args.validation)
    elif normalized_last_updated:
        validation_block = "\n".join(
            [
                f"- Continuity source: MEMORY.md ({normalized_last_updated})",
                "- Re-run the relevant smoke or integration checks before continuing.",
            ]
        )
    else:
        validation_block = "- "

    rendered = template_text.rstrip() + "\n"
    rendered = rendered.replace("# Handoff Snapshot - <title>", f"# Handoff Snapshot - {args.title}", 1)
    rendered = replace_line(rendered, "Timestamp", display_timestamp)
    rendered = replace_line(rendered, "Repo shape", repo_shape)
    rendered = replace_line(rendered, "Active manifest or profile", manifest)
    rendered = replace_line(rendered, "Completed prompt or milestone", args.completed_milestone)
    rendered = replace_line(rendered, "Next intended prompt or phase", args.next_phase)
    rendered = rendered.replace("<current task objective>", objective, 1)
    rendered = replace_section(rendered, "State At Handoff", state_block)
    rendered = replace_section(rendered, "Completed Work", completed_block)
    rendered = replace_section(rendered, "Remaining Work", remaining_block)
    rendered = replace_section(rendered, "Decisions Already Made", decision_block)
    rendered = replace_section(rendered, "Explicitly Not Doing", not_doing_block)
    rendered = replace_section(rendered, "Blockers Or Risks", risk_block)
    rendered = replace_section(rendered, "Exact Files To Inspect Next", next_files_block)
    rendered = replace_section(rendered, "Validation Status", validation_block)

    output_path = handoff_dir / f"{filename_timestamp}-{slug}.md"
    output_path.write_text(rendered, encoding="utf-8")
    print(f"Created {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
