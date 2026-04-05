#!/usr/bin/env python3
"""Manage repo-local runtime state for assistant sessions."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class RuntimeFileSpec:
    path: str
    label: str
    max_lines: int
    max_words: int
    template: str
    example_path: str


@dataclass(frozen=True)
class RuntimeFileState:
    spec: RuntimeFileSpec
    exists: bool
    line_count: int
    word_count: int
    byte_count: int
    mtime: float | None
    age_seconds: float | None
    warnings: tuple[str, ...]
    sections: dict[str, str]


@dataclass(frozen=True)
class GitAnchor:
    commit: str
    timestamp: float | None
    timestamp_text: str
    subject: str
    changed_files: tuple[str, ...]


@dataclass(frozen=True)
class RepoInspection:
    states: tuple[RuntimeFileState, ...]
    warnings: tuple[str, ...]
    git_state: dict[str, object]
    git_anchor: GitAnchor | None
    recent_change_clues: tuple[str, ...]
    next_step_hint: str | None
    next_step_source: str | None
    task_fallback_step: str | None
    plan_review_signal: str
    memory_promotion_hints: tuple[str, ...]


PLACEHOLDER_PATTERNS = (
    re.compile(r"<[^>]+>"),
    re.compile(r"\bTODO\b", flags=re.IGNORECASE),
    re.compile(r"\bTBD\b", flags=re.IGNORECASE),
    re.compile(r"\bfill in\b", flags=re.IGNORECASE),
    re.compile(r"\bname the current\b", flags=re.IGNORECASE),
    re.compile(r"\bstate the active\b", flags=re.IGNORECASE),
    re.compile(r"\bconcrete completion signals\b", flags=re.IGNORECASE),
    re.compile(r"\bnext action\b", flags=re.IGNORECASE),
    re.compile(r"\bfollow-on action\b", flags=re.IGNORECASE),
    re.compile(r"\bsummarize the current working position\b", flags=re.IGNORECASE),
    re.compile(r"\brecord only fresh decisions\b", flags=re.IGNORECASE),
    re.compile(r"\bthe next concrete action a fresh assistant can take\b", flags=re.IGNORECASE),
    re.compile(r"\blist files or areas already explored\b", flags=re.IGNORECASE),
    re.compile(r"^\s*-\s*$", flags=re.MULTILINE),
)

MEMORY_TEMPORARY_PATTERNS = (
    re.compile(r"\bcurrent task\b", flags=re.IGNORECASE),
    re.compile(r"\bnext safe step\b", flags=re.IGNORECASE),
    re.compile(r"\bimmediate steps?\b", flags=re.IGNORECASE),
    re.compile(r"\bblockers?\b", flags=re.IGNORECASE),
    re.compile(r"\btoday\b|\byesterday\b|\btomorrow\b", flags=re.IGNORECASE),
)

RUNTIME_FILES = (
    RuntimeFileSpec(
        path="PLAN.md",
        label="PLAN.md",
        max_lines=220,
        max_words=2400,
        template="""# PLAN.md

## Active Phase
- Name the current milestone or phase.

## Milestones
- Milestone:
  Exit signal:

## Near-Term Focus
- Note only the next few meaningful tracks, not every tiny implementation step.

## Plan Update Triggers
- Update this file when a `.prompts` megaprompt or a major decision reshapes phases, milestones, or the near-to-mid-term roadmap.
- Do not update this file for normal progress inside an already-defined phase.

## Last Updated
- YYYY-MM-DD HH:MM local time
""",
        example_path="PLAN.example.md",
    ),
    RuntimeFileSpec(
        path="context/TASK.md",
        label="context/TASK.md",
        max_lines=120,
        max_words=1400,
        template="""# TASK.md

## Current Slice
- State the active subtask or implementation slice.

## Success Criteria
- Concrete completion signals for this slice.

## Immediate Steps
- Next action.
- Follow-on action.

## Blockers
- None currently.

## Out Of Scope
- Keep the current slice narrow.

## Last Updated
- YYYY-MM-DD HH:MM local time
""",
        example_path="context/TASK.example.md",
    ),
    RuntimeFileSpec(
        path="context/SESSION.md",
        label="context/SESSION.md",
        max_lines=90,
        max_words=1000,
        template="""# SESSION.md

## Current Status
- Summarize the current working position in 2-4 bullets.

## Recent Decisions
- Record only fresh decisions that matter for the next session.

## Active Files
- path/to/file

## Next Safe Step
- The next concrete action a fresh assistant can take without re-discovery.

## Skip Reloading
- List files or areas already explored deeply unless implementation reality changed.

## Last Updated
- YYYY-MM-DD HH:MM local time
""",
        example_path="context/SESSION.example.md",
    ),
    RuntimeFileSpec(
        path="context/MEMORY.md",
        label="context/MEMORY.md",
        max_lines=140,
        max_words=1500,
        template="""# MEMORY.md

## Durable Rules
- Stable assistant behavior expectations for this repo.

## Stable Repo Truths
- Facts that are likely to remain true across sessions.

## Known Pitfalls
- Recurring traps worth remembering.

## Reusable Commands
- Validation:

## Last Updated
- YYYY-MM-DD HH:MM local time
""",
        example_path="context/MEMORY.example.md",
    ),
)

ACTIVE_RUNTIME_PATHS = frozenset(spec.path for spec in RUNTIME_FILES if spec.path != "context/MEMORY.md")
TIME_STALENESS_REVIEW_SECONDS = 24 * 60 * 60
TIME_STALENESS_WARNING_SECONDS = 72 * 60 * 60
MAX_RECENT_CLUES = 6
MAX_MEMORY_HINT_PATHS = 4
PROMPT_PLAN_REVIEW_GRACE_SECONDS = 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage assistant-facing repo-local runtime state.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create missing runtime state files.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing runtime state files.")

    status_parser = subparsers.add_parser("status", help="Summarize runtime-state health without mutating files.")
    status_parser.add_argument("--strict", action="store_true", help="Exit with status 1 when warnings are found.")

    resume_parser = subparsers.add_parser(
        "resume",
        help="Summarize the current working situation for a fresh session without mutating files.",
    )
    resume_parser.add_argument("--strict", action="store_true", help="Exit with status 1 when warnings are found.")

    checkpoint_parser = subparsers.add_parser(
        "checkpoint",
        help="Scaffold missing runtime files and report drift or compaction pressure.",
    )
    checkpoint_parser.add_argument("--force", action="store_true", help="Overwrite existing runtime state files.")
    checkpoint_parser.add_argument("--strict", action="store_true", help="Exit with status 1 when warnings are found.")

    return parser


def candidate_roots(start: Path) -> list[Path]:
    return [start, *start.parents]


def detect_repo_root() -> Path:
    search_starts = [Path.cwd().resolve(), Path(__file__).resolve().parent]
    seen: set[Path] = set()
    for start in search_starts:
        for candidate in candidate_roots(start):
            if candidate in seen:
                continue
            seen.add(candidate)
            markers = (
                candidate / "AGENT.md",
                candidate / "CLAUDE.md",
                candidate / ".git",
            )
            has_tool = (candidate / "scripts/work.py").exists() or (candidate / ".acb/scripts/work.py").exists()
            if any(marker.exists() for marker in markers) and has_tool:
                return candidate
    raise RuntimeError("Could not detect repo root from the current working directory or script location.")


def active_script_label(repo_root: Path) -> str:
    script_path = Path(__file__).resolve()
    try:
        relative = script_path.relative_to(repo_root).as_posix()
    except ValueError:
        relative = "scripts/work.py"
    return f"python3 {relative}"


def parse_sections(text: str) -> dict[str, str]:
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


def has_placeholder(text: str) -> bool:
    return any(pattern.search(text) for pattern in PLACEHOLDER_PATTERNS)


def run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result


def normalize_git_path(value: str) -> str:
    candidate = value.strip()
    if " -> " in candidate:
        return candidate.split(" -> ", 1)[1].strip()
    return candidate


def parse_git_timestamp(raw: str) -> float | None:
    text = raw.strip()
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M:%S %z").timestamp()
    except ValueError:
        return None


def format_timestamp(timestamp: float | None) -> str:
    if timestamp is None:
        return "unknown"
    return datetime.fromtimestamp(timestamp).astimezone().strftime("%Y-%m-%d %H:%M %Z")


def format_age(age_seconds: float | None) -> str:
    if age_seconds is None:
        return "unknown age"
    seconds = max(int(age_seconds), 0)
    if seconds < 60:
        return "under 1 minute old"
    if seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} old"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} old"
    days = seconds // 86400
    return f"{days} day{'s' if days != 1 else ''} old"


def first_actionable_line(section_text: str) -> str | None:
    for raw_line in section_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\s+", "", line)
        line = re.sub(r"^\d+\.\s+", "", line)
        if not line or has_placeholder(line):
            continue
        return line
    return None


def format_path_list(paths: list[str], *, limit: int) -> str:
    display = paths[:limit]
    if not display:
        return ""
    suffix = "" if len(paths) <= limit else f", +{len(paths) - limit} more"
    return ", ".join(display) + suffix


def select_scaffold_content(repo_root: Path, spec: RuntimeFileSpec) -> tuple[str, str]:
    example_path = repo_root / spec.example_path
    if example_path.exists() and example_path.is_file():
        return example_path.read_text(encoding="utf-8"), spec.example_path
    return spec.template, "built-in default"


def collect_git_anchor(repo_root: Path) -> GitAnchor | None:
    log_result = run_git(repo_root, "log", "-1", "--date=iso-local", "--format=%h%x1f%cd%x1f%s")
    if log_result is None or not log_result.stdout.strip():
        return None

    parts = log_result.stdout.strip().split("\x1f", 2)
    if len(parts) != 3:
        return None

    changed_result = run_git(repo_root, "show", "--pretty=format:", "--name-only", "HEAD")
    changed_files = tuple(
        normalize_git_path(line)
        for line in changed_result.stdout.splitlines()
        if changed_result is not None and line.strip()
    )
    timestamp = parse_git_timestamp(parts[1])
    return GitAnchor(
        commit=parts[0].strip(),
        timestamp=timestamp,
        timestamp_text=parts[1].strip(),
        subject=parts[2].strip(),
        changed_files=changed_files,
    )


def collect_git_state(repo_root: Path) -> dict[str, object]:
    status_result = run_git(repo_root, "status", "--short")
    if status_result is None:
        return {"available": False, "changed_files": [], "branch": "", "staged_count": 0, "unstaged_count": 0}

    changed_files: list[str] = []
    staged_count = 0
    unstaged_count = 0
    for line in status_result.stdout.splitlines():
        if not line.strip():
            continue
        changed_files.append(normalize_git_path(line[3:] if len(line) > 3 else line.strip()))
        if len(line) >= 1 and line[0] != " ":
            staged_count += 1
        if len(line) >= 2 and line[1] != " ":
            unstaged_count += 1

    branch_result = run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")
    branch = branch_result.stdout.strip() if branch_result is not None else ""
    return {
        "available": True,
        "changed_files": changed_files,
        "branch": branch,
        "staged_count": staged_count,
        "unstaged_count": unstaged_count,
    }


def inspect_runtime_file(
    repo_root: Path,
    spec: RuntimeFileSpec,
    git_state: dict[str, object],
    git_anchor: GitAnchor | None,
    now: float,
) -> RuntimeFileState:
    path = repo_root / spec.path
    if not path.exists():
        return RuntimeFileState(
            spec=spec,
            exists=False,
            line_count=0,
            word_count=0,
            byte_count=0,
            mtime=None,
            age_seconds=None,
            warnings=(f"missing {spec.label}",),
            sections={},
        )

    text = path.read_text(encoding="utf-8")
    line_count = len(text.splitlines())
    word_count = len(re.findall(r"\S+", text))
    sections = parse_sections(text)
    warnings: list[str] = []
    stat = path.stat()
    age_seconds = max(now - stat.st_mtime, 0.0)

    if line_count > spec.max_lines:
        warnings.append(f"{spec.label} is large ({line_count} lines)")
    if word_count > spec.max_words:
        warnings.append(f"{spec.label} is verbose ({word_count} words)")
    if has_placeholder(text):
        warnings.append(f"{spec.label} still contains template or placeholder text")

    if spec.path == "context/TASK.md":
        for heading in ("Current Slice", "Success Criteria", "Immediate Steps"):
            if not sections.get(heading, "").strip():
                warnings.append(f"context/TASK.md is missing a useful '{heading}' section")
    elif spec.path == "context/SESSION.md":
        if not sections.get("Next Safe Step", "").strip():
            warnings.append("context/SESSION.md is missing a concrete next safe step")
        if not sections.get("Current Status", "").strip():
            warnings.append("context/SESSION.md is missing current status")
    elif spec.path == "context/MEMORY.md":
        if any(pattern.search(text) for pattern in MEMORY_TEMPORARY_PATTERNS):
            warnings.append("context/MEMORY.md looks polluted with short-lived task state")
    elif spec.path == "PLAN.md":
        if not sections.get("Milestones", "").strip():
            warnings.append("PLAN.md does not currently record milestones or phases")

    changed_files = [str(item) for item in git_state.get("changed_files", [])]
    if changed_files:
        existing_changed_paths = []
        for relative in changed_files:
            candidate = repo_root / relative
            if candidate.exists() and candidate.is_file():
                existing_changed_paths.append(candidate)
        if existing_changed_paths and stat.st_mtime + 60 < max(item.stat().st_mtime for item in existing_changed_paths):
            warnings.append(f"{spec.label} looks older than the current changed-file surface")

    if spec.path in ACTIVE_RUNTIME_PATHS:
        if age_seconds >= TIME_STALENESS_WARNING_SECONDS:
            warnings.append(f"{spec.label} is {format_age(age_seconds)}; review it before continuing")
        elif age_seconds >= TIME_STALENESS_REVIEW_SECONDS:
            warnings.append(f"{spec.label} is {format_age(age_seconds)}; give it a quick review before continuing")

    if git_anchor is not None and git_anchor.timestamp is not None and spec.path in ACTIVE_RUNTIME_PATHS:
        if stat.st_mtime + 60 < git_anchor.timestamp:
            warnings.append(f"{spec.label} predates the latest commit anchor")

    return RuntimeFileState(
        spec=spec,
        exists=True,
        line_count=line_count,
        word_count=word_count,
        byte_count=stat.st_size,
        mtime=stat.st_mtime,
        age_seconds=age_seconds,
        warnings=tuple(warnings),
        sections=sections,
    )


def classify_recent_change_clues(git_state: dict[str, object], git_anchor: GitAnchor | None) -> tuple[str, ...]:
    changed_files = [str(item) for item in git_state.get("changed_files", []) if str(item).strip()]
    if changed_files:
        return (
            f"working tree changed: {format_path_list(changed_files, limit=MAX_RECENT_CLUES)}",
        )
    if git_anchor is not None and git_anchor.changed_files:
        return (
            f"last commit touched: {format_path_list(list(git_anchor.changed_files), limit=MAX_RECENT_CLUES)}",
        )
    return ("working tree is clean and no recent git anchor was available",)


def infer_next_step(states: tuple[RuntimeFileState, ...]) -> tuple[str | None, str | None, str | None]:
    state_by_path = {state.spec.path: state for state in states}
    task_state = state_by_path.get("context/TASK.md")
    session_state = state_by_path.get("context/SESSION.md")

    task_step = first_actionable_line(task_state.sections.get("Immediate Steps", "")) if task_state else None
    session_step = first_actionable_line(session_state.sections.get("Next Safe Step", "")) if session_state else None

    if session_step:
        return session_step, "context/SESSION.md -> Next Safe Step", task_step
    if task_step:
        return task_step, "context/TASK.md -> Immediate Steps", None
    return None, None, None


def plan_review_signal(
    repo_root: Path,
    states: tuple[RuntimeFileState, ...],
    git_state: dict[str, object],
    git_anchor: GitAnchor | None,
) -> str:
    plan_state = next(state for state in states if state.spec.path == "PLAN.md")
    if not plan_state.exists:
        return "PLAN.md is missing; create it only if milestone-level roadmap tracking is needed."

    prompt_dir = repo_root / ".prompts"
    prompt_files = [path for path in prompt_dir.glob("*.txt") if prompt_dir.exists() and path.is_file()]
    if prompt_files and plan_state.mtime is not None:
        newest_prompt_mtime = max(path.stat().st_mtime for path in prompt_files)
        if plan_state.mtime + PROMPT_PLAN_REVIEW_GRACE_SECONDS < newest_prompt_mtime:
            return "PLAN review likely: `.prompts/` changed after PLAN.md. Update the plan only if phases or milestones shifted."

    recent_paths = [str(item) for item in git_state.get("changed_files", []) if str(item).strip()]
    if not recent_paths and git_anchor is not None:
        recent_paths = list(git_anchor.changed_files)
    if any(path.startswith(".prompts/") for path in recent_paths):
        return "PLAN review may be warranted because prompt-sequence files changed. Only update it if the roadmap changed materially."

    return "PLAN review probably not needed unless phases, milestones, or the near-to-mid-term roadmap changed."


def build_memory_promotion_hints(git_state: dict[str, object], git_anchor: GitAnchor | None) -> tuple[str, ...]:
    recent_paths = [str(item) for item in git_state.get("changed_files", []) if str(item).strip()]
    source_label = "working tree"
    if not recent_paths and git_anchor is not None:
        recent_paths = list(git_anchor.changed_files)
        source_label = "latest commit"
    if not recent_paths:
        return ()

    hints: list[str] = []

    def matching_paths(predicate: Callable[[str], bool]) -> list[str]:
        return [path for path in recent_paths if predicate(path)]

    assistant_docs = matching_paths(
        lambda path: path in {"AGENT.md", "CLAUDE.md"}
        or path.startswith("docs/")
        or path.startswith("context/anchors/")
        or path.startswith("context/specs/agent/")
    )
    if assistant_docs:
        hints.append(
            "Consider a MEMORY.md update if assistant-facing guidance changed in "
            f"{source_label}: {format_path_list(assistant_docs, limit=MAX_MEMORY_HINT_PATHS)}."
        )

    template_paths = matching_paths(lambda path: path.startswith("templates/"))
    if template_paths:
        hints.append(
            "Consider a MEMORY.md update if repo-local scaffolds now imply new defaults: "
            f"{format_path_list(template_paths, limit=MAX_MEMORY_HINT_PATHS)}."
        )

    generator_paths = matching_paths(
        lambda path: path.startswith("scripts/new_repo.py")
        or path.startswith("scripts/work.py")
        or path.startswith("scripts/acb_")
        or path.startswith("manifests/")
    )
    if generator_paths:
        hints.append(
            "Consider a MEMORY.md update if repo-factory or vendored-runtime behavior changed: "
            f"{format_path_list(generator_paths, limit=MAX_MEMORY_HINT_PATHS)}."
        )

    workflow_paths = matching_paths(
        lambda path: path.startswith(".prompts/")
        or path.startswith("context/workflows/")
        or path.startswith("context/doctrine/")
        or path in {
            "docs/runtime-state-workflow.md",
            "docs/context-boot-sequence.md",
            "docs/session-start.md",
        }
    )
    if workflow_paths:
        hints.append(
            "Consider a MEMORY.md update if standing workflow or prompt-sequence doctrine changed: "
            f"{format_path_list(workflow_paths, limit=MAX_MEMORY_HINT_PATHS)}."
        )

    return tuple(dedupe(hints))


def inspect_repo(repo_root: Path) -> RepoInspection:
    git_state = collect_git_state(repo_root)
    git_anchor = collect_git_anchor(repo_root)
    now = time.time()
    states = tuple(inspect_runtime_file(repo_root, spec, git_state, git_anchor, now) for spec in RUNTIME_FILES)
    warnings = [warning for state in states for warning in state.warnings]

    session_state = next(state for state in states if state.spec.path == "context/SESSION.md")
    task_state = next(state for state in states if state.spec.path == "context/TASK.md")
    if session_state.line_count + task_state.line_count > 180:
        warnings.append("context/TASK.md + context/SESSION.md are broad enough to justify compaction")

    if len([item for item in git_state.get("changed_files", []) if str(item).strip()]) > 12:
        warnings.append("changed-file surface is broad; narrow the active slice before the next handoff")

    prompt_dir = repo_root / ".prompts"
    plan_path = repo_root / "PLAN.md"
    if prompt_dir.exists():
        prompt_files = [path for path in prompt_dir.glob("*.txt") if path.is_file()]
        if prompt_files and plan_path.exists():
            newest_prompt_mtime = max(path.stat().st_mtime for path in prompt_files)
            if plan_path.stat().st_mtime + PROMPT_PLAN_REVIEW_GRACE_SECONDS < newest_prompt_mtime:
                warnings.append(
                    "`.prompts/` changed after PLAN.md; update the plan only if phases or milestones were materially reshaped"
                )

    legacy_memory = repo_root / "MEMORY.md"
    if legacy_memory.exists():
        warnings.append("legacy root MEMORY.md still exists; use context/MEMORY.md for durable runtime memory")

    next_step_hint, next_step_source, task_fallback_step = infer_next_step(states)
    return RepoInspection(
        states=states,
        warnings=tuple(dedupe(warnings)),
        git_state=git_state,
        git_anchor=git_anchor,
        recent_change_clues=classify_recent_change_clues(git_state, git_anchor),
        next_step_hint=next_step_hint,
        next_step_source=next_step_source,
        task_fallback_step=task_fallback_step,
        plan_review_signal=plan_review_signal(repo_root, states, git_state, git_anchor),
        memory_promotion_hints=build_memory_promotion_hints(git_state, git_anchor),
    )


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def ensure_runtime_files(repo_root: Path, *, force: bool) -> list[str]:
    actions: list[str] = []
    for spec in RUNTIME_FILES:
        path = repo_root / spec.path
        path.parent.mkdir(parents=True, exist_ok=True)
        existed = path.exists()
        if existed and not force:
            continue
        content, source = select_scaffold_content(repo_root, spec)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        verb = "Overwrote" if existed else "Created"
        actions.append(f"{verb} {spec.path} from {source}")
    return actions


def print_header(title: str) -> None:
    print(title)
    print("=" * len(title))


def print_git_signals(git_state: dict[str, object], git_anchor: GitAnchor | None, recent_change_clues: tuple[str, ...]) -> None:
    print("")
    print("Git signals:")
    if git_anchor is not None:
        anchor_time = format_timestamp(git_anchor.timestamp) if git_anchor.timestamp is not None else git_anchor.timestamp_text
        print(f"- Last commit: {git_anchor.commit} at {anchor_time} - {git_anchor.subject}")
    else:
        print("- Last commit: unavailable")
    for clue in recent_change_clues:
        print(f"- Recent clue: {clue}")


def print_state_summary(repo_root: Path, script_cmd: str, states: tuple[RuntimeFileState, ...], git_state: dict[str, object], git_anchor: GitAnchor | None) -> None:
    branch = str(git_state.get("branch", "")).strip()
    branch_text = branch if branch else "unknown"
    changed_count = len([item for item in git_state.get("changed_files", []) if str(item).strip()])

    print(f"Repo root: {repo_root}")
    print(f"Runtime command: {script_cmd}")
    print(f"Git branch: {branch_text}")
    print(
        "Git working tree: "
        f"{changed_count} changed file(s), "
        f"{git_state.get('staged_count', 0)} staged, "
        f"{git_state.get('unstaged_count', 0)} unstaged"
    )
    print("")
    print("Runtime state files:")
    for state in states:
        status = "present" if state.exists else "missing"
        if state.exists:
            details = f"{state.line_count} lines, {state.word_count} words, {format_age(state.age_seconds)}"
            if git_anchor is not None and git_anchor.timestamp is not None and state.mtime is not None and state.mtime + 60 < git_anchor.timestamp:
                details += ", older than latest commit"
        else:
            details = "not created yet"
        print(f"- {state.spec.label}: {status} ({details})")


def print_inferred_signals(inspection: RepoInspection) -> None:
    print("")
    print("Working signals:")
    if inspection.next_step_hint and inspection.next_step_source:
        print(f"- Next concrete step: {inspection.next_step_hint} ({inspection.next_step_source})")
    else:
        print("- Next concrete step: no clear step was inferred from runtime notes")
    if inspection.task_fallback_step and inspection.next_step_hint != inspection.task_fallback_step:
        print(f"- TASK fallback step: {inspection.task_fallback_step}")
    print(f"- PLAN review: {inspection.plan_review_signal}")
    if inspection.memory_promotion_hints:
        for hint in inspection.memory_promotion_hints:
            print(f"- Memory promotion hint: {hint}")
    else:
        print("- Memory promotion hint: none from the current working tree or latest commit surface")


def print_resume_guidance(script_cmd: str, states: tuple[RuntimeFileState, ...]) -> None:
    state_by_path = {state.spec.path: state for state in states}
    print("")
    print("Next reads:")
    if state_by_path["context/TASK.md"].exists:
        print("- Read `context/TASK.md` for the current active slice.")
    else:
        print(f"- Run `{script_cmd} checkpoint` to scaffold `context/TASK.md` before continuing.")
    if state_by_path["context/SESSION.md"].exists:
        print("- Read `context/SESSION.md` for the current status and next safe step.")
    if state_by_path["context/MEMORY.md"].exists:
        print("- Read `context/MEMORY.md` only if durable repo-local truths or guardrails matter.")
    if state_by_path["PLAN.md"].exists:
        print("- Read `PLAN.md` when milestone context, phase changes, or `.prompts` roadmap shifts matter.")
    else:
        print("- Create `PLAN.md` only when the work needs milestone-level roadmap state.")
    print("- Keep any ad hoc session checklist or scratch execution plan in `tmp/*.md`, not in `PLAN.md`.")

    print("")
    print("Checkpoint reminders:")
    print(f"- Use `{script_cmd} checkpoint` after meaningful changes, before ending a session, and before a likely handoff.")
    print("- Keep `context/SESSION.md` concise and action-oriented.")
    print("- Use `tmp/*.md` for session-scoped checklists or ad hoc work plans that should stay local.")
    print("- Update `PLAN.md` only when phases, milestones, or the near-to-mid-term roadmap changed materially.")


def print_warnings(warnings: tuple[str, ...]) -> None:
    print("")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("Warnings:")
        print("- none")


def handle_init(repo_root: Path, force: bool) -> int:
    print_header("Runtime State Init")
    actions = ensure_runtime_files(repo_root, force=force)
    if actions:
        for action in actions:
            print(action)
    else:
        print("All canonical runtime files already exist.")
    return 0


def handle_status(repo_root: Path, script_cmd: str, strict: bool) -> int:
    print_header("Runtime State Status")
    inspection = inspect_repo(repo_root)
    print_state_summary(repo_root, script_cmd, inspection.states, inspection.git_state, inspection.git_anchor)
    print_git_signals(inspection.git_state, inspection.git_anchor, inspection.recent_change_clues)
    print_inferred_signals(inspection)
    print_warnings(inspection.warnings)
    return 1 if strict and inspection.warnings else 0


def handle_resume(repo_root: Path, script_cmd: str, strict: bool) -> int:
    print_header("Runtime Resume")
    inspection = inspect_repo(repo_root)
    print_state_summary(repo_root, script_cmd, inspection.states, inspection.git_state, inspection.git_anchor)
    print_git_signals(inspection.git_state, inspection.git_anchor, inspection.recent_change_clues)
    print_inferred_signals(inspection)
    print_warnings(inspection.warnings)
    print_resume_guidance(script_cmd, inspection.states)
    return 1 if strict and inspection.warnings else 0


def handle_checkpoint(repo_root: Path, script_cmd: str, force: bool, strict: bool) -> int:
    print_header("Runtime Checkpoint")
    actions = ensure_runtime_files(repo_root, force=force)
    if actions:
        print("Scaffold actions:")
        for action in actions:
            print(f"- {action}")
        print("")
    else:
        print("Scaffold actions:")
        print("- no file scaffolding was needed")
        print("")

    inspection = inspect_repo(repo_root)
    print_state_summary(repo_root, script_cmd, inspection.states, inspection.git_state, inspection.git_anchor)
    print_git_signals(inspection.git_state, inspection.git_anchor, inspection.recent_change_clues)
    print_inferred_signals(inspection)
    print_warnings(inspection.warnings)
    print("")
    print("Checkpoint doctrine:")
    print("- Run checkpoints after meaningful code or doc changes, after a completed subtask, before ending a session, and before switching branches or worktrees.")
    print("- Refresh `context/SESSION.md` when it is stale, bloated, or missing a clear next safe step.")
    print("- Keep prompt-session checklists or ad hoc execution plans in `tmp/*.md`, not in `PLAN.md`.")
    print("- Refresh `PLAN.md` when a `.prompts` megaprompt or major decision materially changes phases or milestones.")
    print("- Keep `context/MEMORY.md` durable; move active-step sludge back into `context/TASK.md` or `context/SESSION.md`.")
    print("")
    print("Note: existing runtime notes were not rewritten automatically.")
    return 1 if strict and inspection.warnings else 0


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv[1:])
    try:
        repo_root = detect_repo_root()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    script_cmd = active_script_label(repo_root)
    if args.command == "init":
        return handle_init(repo_root, force=args.force)
    if args.command == "status":
        return handle_status(repo_root, script_cmd, strict=args.strict)
    if args.command == "resume":
        return handle_resume(repo_root, script_cmd, strict=args.strict)
    if args.command == "checkpoint":
        return handle_checkpoint(repo_root, script_cmd, force=args.force, strict=args.strict)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
