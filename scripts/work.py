#!/usr/bin/env python3
"""Manage repo-local runtime state for assistant sessions."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


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


@dataclass(frozen=True)
class ProjectFiles:
    project_dir: Path
    work_state: Path
    session_queue: Path
    commit_log: Path
    rate_limits: Path
    run_history: Path


@dataclass(frozen=True)
class RecentCommitEntry:
    short_hash: str
    date_text: str
    subject: str
    prompt_prefix: str | None


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
PROMPT_PREFIX_PATTERN = re.compile(r"(\[PROMPT_(\d+)\])")
PROMPT_FILE_PATTERN = re.compile(r"^PROMPT_(\d+)\.txt$")


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

    init_project_parser = subparsers.add_parser(
        "init-project",
        help="Initialize local operator-console state for this repo.",
    )
    init_project_parser.add_argument("--slug", help="Project slug. Defaults to the repo root directory name.")
    init_project_parser.add_argument("--force", action="store_true", help="Overwrite existing operator-console files.")

    next_parser = subparsers.add_parser(
        "next",
        help="Show the next operator session briefing without mutating files.",
    )
    next_parser.add_argument("--slug", help="Project slug. Defaults to the repo root directory name.")

    start_parser = subparsers.add_parser(
        "start",
        help="Mark a prompt as started in the local operator console.",
    )
    start_parser.add_argument("prompt_file", help="Prompt filename, for example PROMPT_92.txt.")
    start_parser.add_argument("--assistant", help="Assistant name for the run history entry.")
    start_parser.add_argument("--slug", help="Project slug. Defaults to the repo root directory name.")

    pause_parser = subparsers.add_parser(
        "pause",
        help="Mark a prompt as paused in the local operator console.",
    )
    pause_parser.add_argument("prompt_file", help="Prompt filename, for example PROMPT_92.txt.")
    pause_parser.add_argument("--reason", help="Why the prompt was paused.")
    pause_parser.add_argument("--slug", help="Project slug. Defaults to the repo root directory name.")

    done_parser = subparsers.add_parser(
        "done",
        help="Mark a prompt as done in the local operator console.",
    )
    done_parser.add_argument("prompt_file", help="Prompt filename, for example PROMPT_92.txt.")
    done_parser.add_argument("--slug", help="Project slug. Defaults to the repo root directory name.")

    verify_parser = subparsers.add_parser(
        "verify",
        help="Run operator-console and prompt-discipline consistency checks.",
    )
    verify_parser.add_argument("--slug", help="Project slug. Defaults to the repo root directory name.")

    recent_commits_parser = subparsers.add_parser(
        "recent-commits",
        help="Show recent commits grouped by prompt prefix.",
    )
    recent_commits_parser.add_argument("--count", type=int, default=15, help="How many recent commits to show.")
    recent_commits_parser.add_argument("--slug", help="Project slug. Defaults to the repo root directory name.")

    log_quota_parser = subparsers.add_parser(
        "log-quota",
        help="Record operator-observed quota information for an assistant.",
    )
    log_quota_parser.add_argument("--assistant", required=True, help="Assistant key: claude, codex, or gemini.")
    log_quota_parser.add_argument("--used-pct-5h", type=float, help="Claude 5-hour usage percent.")
    log_quota_parser.add_argument("--reset-at-5h", help="Claude 5-hour reset timestamp.")
    log_quota_parser.add_argument("--used-pct-7d", type=float, help="Claude 7-day usage percent.")
    log_quota_parser.add_argument("--reset-at-7d", help="Claude 7-day reset timestamp.")
    log_quota_parser.add_argument("--session-status", help="Session status, used primarily for codex.")
    log_quota_parser.add_argument("--notes", help="Operator notes about quota state.")
    log_quota_parser.add_argument("--slug", help="Project slug. Defaults to the repo root directory name.")

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


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_project_dir(repo_root: Path, slug: str | None = None) -> Path:
    project_slug = slug or repo_root.name
    return repo_root / "work" / "projects" / project_slug


def get_project_files(repo_root: Path, slug: str | None = None) -> ProjectFiles:
    project_dir = get_project_dir(repo_root, slug=slug)
    return ProjectFiles(
        project_dir=project_dir,
        work_state=project_dir / "WORK_STATE.json",
        session_queue=project_dir / "SESSION_QUEUE.md",
        commit_log=project_dir / "COMMIT_LOG.md",
        rate_limits=project_dir / "RATE_LIMITS.json",
        run_history=project_dir / "RUN_HISTORY.md",
    )


def read_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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


def format_optional_pct(value: Any) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return f"{value}%"


def prompt_prefix_from_text(text: str) -> str | None:
    match = PROMPT_PREFIX_PATTERN.search(text)
    return match.group(1) if match else None


def prompt_number_from_filename(prompt_file: str) -> str | None:
    match = PROMPT_FILE_PATTERN.match(prompt_file.strip())
    return match.group(1) if match else None


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


def collect_recent_commits(repo_root: Path, *, count: int) -> list[RecentCommitEntry]:
    result = run_git(repo_root, "log", f"-{count}", "--date=short", "--format=%h%x1f%cd%x1f%s")
    if result is None:
        return []

    commits: list[RecentCommitEntry] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f", 2)
        if len(parts) != 3:
            continue
        commits.append(
            RecentCommitEntry(
                short_hash=parts[0].strip(),
                date_text=parts[1].strip(),
                subject=parts[2].strip(),
                prompt_prefix=prompt_prefix_from_text(parts[2].strip()),
            )
        )
    return commits


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


def default_prompt_entry(prompt_file: str) -> dict[str, Any]:
    return {
        "prompt_file": prompt_file,
        "status": "pending",
        "priority": 50,
        "theme": "",
        "depends_on": [],
        "notes": "",
    }


def default_work_state(repo_root: Path, slug: str | None = None) -> dict[str, Any]:
    git_state = collect_git_state(repo_root)
    return {
        "project_slug": slug or repo_root.name,
        "repo_root": str(repo_root),
        "active_branch": str(git_state.get("branch", "")).strip() or "unknown",
        "current_prompt": None,
        "prompt_queue": [],
        "last_completed_prompt": None,
        "last_started_prompt": None,
        "last_paused_prompt": None,
        "last_resume_summary": None,
        "repo_dirty": bool(git_state.get("changed_files")),
        "last_known_head": None,
        "last_known_head_subject": None,
        "checkpoint_required": False,
        "validation_state": {
            "last_smoke_test_status": None,
            "last_smoke_test_at": None,
            "last_verify_status": None,
            "last_verify_at": None,
        },
        "complexity_budget": {
            "status": "unknown",
            "score": 0,
            "notes": "",
            "measured_at": None,
        },
        "quota_state": {
            "ready_for_next_prompt": True,
            "notes": "",
        },
        "updated_at": None,
    }


def default_rate_limits() -> dict[str, Any]:
    return {
        "assistants": {
            "claude": {
                "plan": "",
                "five_hour_used_pct": None,
                "five_hour_reset_at": None,
                "seven_day_used_pct": None,
                "seven_day_reset_at": None,
                "last_checked_at": None,
                "source": "manual",
                "notes": "",
            },
            "codex": {
                "plan": "",
                "session_status": None,
                "last_checked_at": None,
                "source": "manual",
                "notes": "",
            },
            "gemini": {
                "plan": "",
                "last_checked_at": None,
                "source": "manual",
                "notes": "",
            },
        },
        "policy": {
            "do_not_start_if_claude_five_hour_used_pct_gte": 72,
            "do_not_start_if_claude_seven_day_used_pct_gte": 85,
            "prefer_pause_if_near_limit": True,
        },
        "updated_at": None,
    }


def default_session_queue_text(timestamp: str | None = None) -> str:
    ts = timestamp or "<timestamp>"
    return (
        "# Session Queue\n\n"
        "Generated from WORK_STATE.json. Do not edit directly — use `work.py` commands.\n\n"
        "| # | Prompt File | Status | Priority | Theme | Notes |\n"
        "|---|-------------|--------|----------|-------|-------|\n\n"
        f"Last updated: {ts}\n"
    )


def default_commit_log_text() -> str:
    return (
        "# Commit Log\n\n"
        "Prompt-boundary commit record. Updated by `work.py done`.\n"
    )


def default_run_history_text() -> str:
    return (
        "# Run History\n\n"
        "| Datetime | Prompt | Event | Assistant | Notes | Head Before | Head After |\n"
        "|----------|--------|-------|-----------|-------|-------------|------------|\n"
    )


def default_project_file_contents(repo_root: Path, slug: str | None = None) -> dict[str, str]:
    work_state = default_work_state(repo_root, slug=slug)
    rate_limits = default_rate_limits()
    return {
        "WORK_STATE.json": json.dumps(work_state, indent=2, ensure_ascii=False) + "\n",
        "SESSION_QUEUE.md": default_session_queue_text(work_state["updated_at"]),
        "COMMIT_LOG.md": default_commit_log_text(),
        "RATE_LIMITS.json": json.dumps(rate_limits, indent=2, ensure_ascii=False) + "\n",
        "RUN_HISTORY.md": default_run_history_text(),
    }


def load_work_state(repo_root: Path, slug: str | None = None) -> dict[str, Any] | None:
    path = get_project_files(repo_root, slug=slug).work_state
    if not path.exists():
        return None
    return read_json_file(path)


def save_work_state(repo_root: Path, state_dict: dict[str, Any], slug: str | None = None) -> None:
    state_dict["updated_at"] = iso_now()
    write_json_file(get_project_files(repo_root, slug=slug).work_state, state_dict)


def load_rate_limits(repo_root: Path, slug: str | None = None) -> dict[str, Any]:
    path = get_project_files(repo_root, slug=slug).rate_limits
    if not path.exists():
        return default_rate_limits()
    return read_json_file(path)


def save_rate_limits(repo_root: Path, payload: dict[str, Any], slug: str | None = None) -> None:
    payload["updated_at"] = iso_now()
    write_json_file(get_project_files(repo_root, slug=slug).rate_limits, payload)


def ensure_prompt_entry(state: dict[str, Any], prompt_file: str) -> dict[str, Any]:
    queue = state.setdefault("prompt_queue", [])
    for entry in queue:
        if entry.get("prompt_file") == prompt_file:
            return entry
    entry = default_prompt_entry(prompt_file)
    queue.append(entry)
    return entry


def next_pending_prompt(state: dict[str, Any]) -> dict[str, Any] | None:
    queue = sorted(
        [entry for entry in state.get("prompt_queue", []) if entry.get("status") == "pending"],
        key=lambda entry: (entry.get("priority", 50), entry.get("prompt_file", "")),
    )
    return queue[0] if queue else None


def write_session_queue_markdown(project_files: ProjectFiles, state: dict[str, Any]) -> None:
    lines = [
        "# Session Queue",
        "",
        "Generated from WORK_STATE.json. Do not edit directly — use `work.py` commands.",
        "",
        "| # | Prompt File | Status | Priority | Theme | Notes |",
        "|---|-------------|--------|----------|-------|-------|",
    ]
    for index, entry in enumerate(
        sorted(state.get("prompt_queue", []), key=lambda item: (item.get("priority", 50), item.get("prompt_file", ""))),
        start=1,
    ):
        lines.append(
            "| "
            f"{index} | {entry.get('prompt_file', '')} | {entry.get('status', '')} | "
            f"{entry.get('priority', '')} | {entry.get('theme', '')} | {entry.get('notes', '')} |"
        )
    lines.extend(["", f"Last updated: {state.get('updated_at') or '<timestamp>'}", ""])
    project_files.session_queue.write_text("\n".join(lines), encoding="utf-8")


def append_run_history(project_files: ProjectFiles, *, timestamp: str, prompt_file: str, event: str, assistant: str, notes: str, head_before: str, head_after: str) -> None:
    if not project_files.run_history.exists():
        project_files.run_history.write_text(default_run_history_text(), encoding="utf-8")
    row = f"| {timestamp} | {prompt_file} | {event} | {assistant} | {notes} | {head_before} | {head_after} |\n"
    with project_files.run_history.open("a", encoding="utf-8") as handle:
        handle.write(row)


def read_run_history_rows(project_files: ProjectFiles) -> list[str]:
    if not project_files.run_history.exists():
        return []
    rows: list[str] = []
    for line in project_files.run_history.read_text(encoding="utf-8").splitlines():
        striped = line.strip()
        if striped.startswith("|") and "Datetime" not in striped and "---" not in striped:
            rows.append(striped)
    return rows


def update_commit_log(project_files: ProjectFiles, *, prompt_file: str, status: str, timestamp: str, commits: list[RecentCommitEntry], notes: str = "") -> None:
    if not project_files.commit_log.exists():
        project_files.commit_log.write_text(default_commit_log_text(), encoding="utf-8")
    block = [
        "",
        f"## {prompt_file} — {status} — {timestamp}",
        f"- Commits: {', '.join(commit.short_hash for commit in commits) if commits else 'none found'}",
        f"- Notes: {notes}",
    ]
    with project_files.commit_log.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(block) + "\n")


def find_recent_prompt_commits(repo_root: Path, prompt_file: str) -> list[RecentCommitEntry]:
    prompt_number = prompt_number_from_filename(prompt_file)
    if prompt_number is None:
        return []
    prefix = f"[PROMPT_{prompt_number}]"
    commits = collect_recent_commits(repo_root, count=100)
    return [commit for commit in commits if commit.prompt_prefix == prefix]


def load_operator_state_or_guidance(repo_root: Path, slug: str | None = None) -> tuple[dict[str, Any] | None, ProjectFiles]:
    project_files = get_project_files(repo_root, slug=slug)
    return load_work_state(repo_root, slug=slug), project_files


def latest_prompt_summary_path(repo_root: Path) -> Path | None:
    commits = collect_recent_commits(repo_root, count=20)
    for commit in commits:
        if commit.prompt_prefix is None:
            continue
        number_match = re.search(r"PROMPT_(\d+)", commit.prompt_prefix)
        if not number_match:
            continue
        prompt_number = number_match.group(1)
        for suffix in ("resume", "completion"):
            candidate = repo_root / "memory" / "summaries" / f"PROMPT_{prompt_number}_{suffix}.md"
            if candidate.exists():
                return candidate
        return None
    return None


def quota_policy_result(rate_limits: dict[str, Any]) -> tuple[bool, str]:
    assistants = rate_limits.get("assistants", {})
    claude = assistants.get("claude", {})
    policy = rate_limits.get("policy", {})
    five_hour_used = claude.get("five_hour_used_pct")
    seven_day_used = claude.get("seven_day_used_pct")
    five_hour_limit = policy.get("do_not_start_if_claude_five_hour_used_pct_gte", 72)
    seven_day_limit = policy.get("do_not_start_if_claude_seven_day_used_pct_gte", 85)
    if five_hour_used is None or seven_day_used is None:
        return True, "quota unknown — consider logging with `work.py log-quota`"
    if five_hour_used >= five_hour_limit:
        return False, f"Claude 5h usage is {five_hour_used}% (threshold: {five_hour_limit}%)"
    if seven_day_used >= seven_day_limit:
        return False, f"Claude 7d usage is {seven_day_used}% (threshold: {seven_day_limit}%)"
    return True, "within configured thresholds"


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


def print_resume_guidance(repo_root: Path, script_cmd: str, states: tuple[RuntimeFileState, ...]) -> None:
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
    print("Memory summaries:")
    summary_path = latest_prompt_summary_path(repo_root)
    if summary_path is not None:
        print(f"- {summary_path.relative_to(repo_root).as_posix()} exists and may contain checkpoint context")
    else:
        print("- none found")

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


def print_missing_project_guidance(script_cmd: str) -> None:
    print("Operator console state is not initialized for this repo.")
    print(f"Run `{script_cmd} init-project` first.")


def handle_init_project(repo_root: Path, slug: str | None, force: bool) -> int:
    project_files = get_project_files(repo_root, slug=slug)
    project_files.project_dir.mkdir(parents=True, exist_ok=True)
    contents = default_project_file_contents(repo_root, slug=slug)
    print(f"Work Project Init: {project_files.project_dir.name}")
    for name, content in contents.items():
        path = project_files.project_dir / name
        if path.exists() and not force:
            print(f"- Skipped (exists): {name}")
            continue
        path.write_text(content, encoding="utf-8")
        print(f"- Created: {name}")
    print(f"- Project dir: {project_files.project_dir}")
    return 0


def handle_next(repo_root: Path, script_cmd: str, slug: str | None) -> int:
    state, project_files = load_operator_state_or_guidance(repo_root, slug=slug)
    if state is None:
        print_missing_project_guidance(script_cmd)
        return 0

    inspection = inspect_repo(repo_root)
    rate_limits = load_rate_limits(repo_root, slug=slug)
    ready, policy_reason = quota_policy_result(rate_limits)
    quota_state = state.get("quota_state", {})
    claude = rate_limits.get("assistants", {}).get("claude", {})
    next_prompt = next_pending_prompt(state)
    summary_path = None
    if next_prompt is not None:
        prompt_number = prompt_number_from_filename(str(next_prompt.get("prompt_file", "")))
        if prompt_number is not None:
            resume_candidate = repo_root / "memory" / "summaries" / f"PROMPT_{prompt_number}_resume.md"
            if resume_candidate.exists():
                summary_path = resume_candidate
    if summary_path is None:
        summary_path = latest_prompt_summary_path(repo_root)

    run_history_rows = read_run_history_rows(project_files)[-3:]
    print_header("Next Session Briefing")
    print(f"Project: {state.get('project_slug', project_files.project_dir.name)}")
    branch = str(inspection.git_state.get("branch", "")).strip() or "unknown"
    print(f"Branch:  {branch}")
    if inspection.git_anchor is not None:
        print(f"Head:    {inspection.git_anchor.commit} {inspection.git_anchor.subject}")
    else:
        print("Head:    unavailable")
    changed_count = len([item for item in inspection.git_state.get("changed_files", []) if str(item).strip()])
    print("")
    print(f"Repo:    {'clean' if changed_count == 0 else f'{changed_count} changed files'}")
    print("")
    print(f"Next Prompt:   {next_prompt.get('prompt_file') if next_prompt else 'none pending'}")
    print(f"Theme:         {next_prompt.get('theme') if next_prompt and next_prompt.get('theme') else ''}")
    depends_on = next_prompt.get("depends_on", []) if next_prompt else []
    print(f"Depends On:    {', '.join(depends_on) if depends_on else 'none'}")
    print("")
    print("Quota Check:")
    print(f"- Ready:       {'yes' if ready and quota_state.get('ready_for_next_prompt', True) else 'no'}")
    print(
        f"- Claude 5h:   {format_optional_pct(claude.get('five_hour_used_pct'))} "
        f"(threshold: {rate_limits.get('policy', {}).get('do_not_start_if_claude_five_hour_used_pct_gte', 72)}%)"
    )
    print(
        f"- Claude 7d:   {format_optional_pct(claude.get('seven_day_used_pct'))} "
        f"(threshold: {rate_limits.get('policy', {}).get('do_not_start_if_claude_seven_day_used_pct_gte', 85)}%)"
    )
    notes = quota_state.get("notes") or policy_reason
    print(f"- Notes:       {notes}")
    print("")
    print(f"Resume Summary:  {summary_path.relative_to(repo_root).as_posix() if summary_path is not None else 'none'}")
    print("")
    print("Recommended Action:")
    if next_prompt is None:
        print("- No pending prompts")
    elif "quota unknown" in policy_reason:
        print(f"- Safe to start {next_prompt.get('prompt_file')} (quota unknown — consider logging with `work.py log-quota`)")
    elif ready and quota_state.get("ready_for_next_prompt", True):
        print(f"- Safe to start {next_prompt.get('prompt_file')}")
    else:
        print(f"- Wait: {notes}")
    print("")
    print(f"Run History:     {'none' if not run_history_rows else ''}")
    for row in run_history_rows:
        print(f"  {row}")
    return 0


def handle_start(repo_root: Path, slug: str | None, prompt_file: str, assistant: str | None) -> int:
    state = load_work_state(repo_root, slug=slug)
    if state is None:
        print("WORK_STATE.json is missing. Run `python3 scripts/work.py init-project` first.")
        return 1
    project_files = get_project_files(repo_root, slug=slug)
    entry = ensure_prompt_entry(state, prompt_file)
    for queue_entry in state.get("prompt_queue", []):
        if queue_entry.get("prompt_file") == prompt_file:
            queue_entry["status"] = "in_progress"
        elif queue_entry.get("status") == "in_progress":
            queue_entry["status"] = "paused"
    inspection = inspect_repo(repo_root)
    entry["status"] = "in_progress"
    state["current_prompt"] = prompt_file
    state["last_started_prompt"] = prompt_file
    state["active_branch"] = str(inspection.git_state.get("branch", "")).strip() or "unknown"
    state["repo_dirty"] = bool(inspection.git_state.get("changed_files"))
    state["last_known_head"] = inspection.git_anchor.commit if inspection.git_anchor is not None else None
    state["last_known_head_subject"] = inspection.git_anchor.subject if inspection.git_anchor is not None else None
    save_work_state(repo_root, state, slug=slug)
    write_session_queue_markdown(project_files, state)
    timestamp = state["updated_at"]
    head_text = (
        f"{inspection.git_anchor.commit} {inspection.git_anchor.subject}"
        if inspection.git_anchor is not None
        else "unavailable"
    )
    append_run_history(
        project_files,
        timestamp=timestamp,
        prompt_file=prompt_file,
        event="start",
        assistant=assistant or "unspecified",
        notes="",
        head_before=head_text,
        head_after=head_text,
    )
    print(f"Started: {prompt_file}")
    print(f"Assistant: {assistant or 'unspecified'}")
    print(f"Head at start: {head_text}")
    print("RUN_HISTORY.md: updated")
    print("WORK_STATE.json: updated")
    print("")
    print("Next: Open a fresh assistant session and paste the prompt.")
    print("Boot: Run `python3 scripts/work.py resume` in that session.")
    print(f'Checkpoint: When pausing, run `work.py pause {prompt_file} --reason "..."`.')
    return 0


def handle_pause(repo_root: Path, slug: str | None, prompt_file: str, reason: str | None) -> int:
    state = load_work_state(repo_root, slug=slug)
    if state is None:
        print("WORK_STATE.json is missing. Run `python3 scripts/work.py init-project` first.")
        return 1
    project_files = get_project_files(repo_root, slug=slug)
    entry = ensure_prompt_entry(state, prompt_file)
    entry["status"] = "paused"
    state["current_prompt"] = None
    state["last_paused_prompt"] = prompt_file
    inspection = inspect_repo(repo_root)
    state["repo_dirty"] = bool(inspection.git_state.get("changed_files"))
    state["last_known_head"] = inspection.git_anchor.commit if inspection.git_anchor is not None else None
    state["last_known_head_subject"] = inspection.git_anchor.subject if inspection.git_anchor is not None else None
    save_work_state(repo_root, state, slug=slug)
    write_session_queue_markdown(project_files, state)
    timestamp = state["updated_at"]
    head_text = (
        f"{inspection.git_anchor.commit} {inspection.git_anchor.subject}"
        if inspection.git_anchor is not None
        else "unavailable"
    )
    append_run_history(
        project_files,
        timestamp=timestamp,
        prompt_file=prompt_file,
        event="pause",
        assistant="unspecified",
        notes=reason or "not specified",
        head_before=head_text,
        head_after=head_text,
    )
    print(f"Paused: {prompt_file}")
    print(f"Reason: {reason or 'not specified'}")
    print("RUN_HISTORY.md: updated")
    print("")
    print("IMPORTANT: Write a resume summary before ending this session.")
    print(f"Expected path: memory/summaries/{prompt_file.replace('.txt', '_resume.md')}")
    print("This file is the primary handoff for the next fresh session.")
    return 0


def handle_done(repo_root: Path, slug: str | None, prompt_file: str) -> int:
    state = load_work_state(repo_root, slug=slug)
    if state is None:
        print("WORK_STATE.json is missing. Run `python3 scripts/work.py init-project` first.")
        return 1
    project_files = get_project_files(repo_root, slug=slug)
    entry = ensure_prompt_entry(state, prompt_file)
    entry["status"] = "done"
    state["current_prompt"] = None
    state["last_completed_prompt"] = prompt_file
    inspection = inspect_repo(repo_root)
    state["repo_dirty"] = bool(inspection.git_state.get("changed_files"))
    state["last_known_head"] = inspection.git_anchor.commit if inspection.git_anchor is not None else None
    state["last_known_head_subject"] = inspection.git_anchor.subject if inspection.git_anchor is not None else None
    commits = find_recent_prompt_commits(repo_root, prompt_file)
    save_work_state(repo_root, state, slug=slug)
    write_session_queue_markdown(project_files, state)
    timestamp = state["updated_at"]
    head_text = (
        f"{inspection.git_anchor.commit} {inspection.git_anchor.subject}"
        if inspection.git_anchor is not None
        else "unavailable"
    )
    append_run_history(
        project_files,
        timestamp=timestamp,
        prompt_file=prompt_file,
        event="done",
        assistant="unspecified",
        notes="",
        head_before=head_text,
        head_after=head_text,
    )
    update_commit_log(project_files, prompt_file=prompt_file, status="done", timestamp=timestamp, commits=commits)
    print(f"Done: {prompt_file}")
    print(
        "Commits found: "
        + (", ".join(f"{commit.short_hash} {commit.prompt_prefix}" for commit in commits) if commits else "none")
    )
    print("COMMIT_LOG.md: updated")
    print("RUN_HISTORY.md: updated")
    completion_summary = repo_root / "memory" / "summaries" / prompt_file.replace(".txt", "_completion.md")
    if not completion_summary.exists():
        print("")
        print("WARNING:")
        print(f"No {completion_summary.relative_to(repo_root).as_posix()} found.")
        print("Consider writing one before starting the next prompt.")
    next_prompt = next_pending_prompt(state)
    print("")
    print(f"Next prompt in queue: {next_prompt.get('prompt_file') if next_prompt else 'none'}")
    print("Run `work.py next` for the full briefing.")
    return 0


def handle_verify(repo_root: Path, script_cmd: str, slug: str | None) -> int:
    _state, _project_files = load_operator_state_or_guidance(repo_root, slug=slug)
    inspection = inspect_repo(repo_root)
    changed_count = len([item for item in inspection.git_state.get("changed_files", []) if str(item).strip()])
    staged_count = int(inspection.git_state.get("staged_count", 0))
    unstaged_count = int(inspection.git_state.get("unstaged_count", 0))
    commits = collect_recent_commits(repo_root, count=5)
    prefixed_count = len([commit for commit in commits if commit.prompt_prefix is not None])
    commit_warnings: list[str] = []
    if len([commit for commit in commits[:3] if commit.prompt_prefix is not None]) == 0:
        commit_warnings.append("none of the last 3 commits follow the [PROMPT_XX] convention")
    state = load_work_state(repo_root, slug=slug)
    work_state_message = "consistent"
    if state is not None:
        current_prompt = state.get("current_prompt")
        in_progress = [entry.get("prompt_file") for entry in state.get("prompt_queue", []) if entry.get("status") == "in_progress"]
        if current_prompt is not None and current_prompt not in in_progress:
            work_state_message = "warning: current_prompt does not match an in-progress queue entry"
        elif any(prompt != current_prompt for prompt in in_progress):
            work_state_message = "warning: queue has an in-progress prompt that does not match current_prompt"
    memory_missing: list[str] = []
    if state is not None:
        for entry in state.get("prompt_queue", []):
            if entry.get("status") == "done":
                summary = repo_root / "memory" / "summaries" / str(entry.get("prompt_file", "")).replace(".txt", "_completion.md")
                if not summary.exists():
                    memory_missing.append(str(entry.get("prompt_file")))
    validate_context = repo_root / "scripts" / "validate_context.py"
    run_verification = repo_root / "scripts" / "run_verification.py"
    warnings_present = changed_count > 10 or bool(commit_warnings) or work_state_message != "consistent" or bool(memory_missing)
    print_header("Verify Report")
    cleanliness = "clean" if changed_count == 0 else f"{changed_count} changes ({staged_count} staged, {unstaged_count} unstaged)"
    print(f"Repo cleanliness:   {cleanliness}")
    print(f"Commit discipline:  {prefixed_count}/5 recent commits follow [PROMPT_XX] convention")
    print(f"Work state:         {work_state_message}")
    memory_summary_status = "complete" if not memory_missing else "missing: " + ", ".join(memory_missing)
    print(f"Memory summaries:   {memory_summary_status}")
    if changed_count > 10:
        print("Warning: repo has more than 10 changed files")
    for warning in commit_warnings:
        print(f"Warning: {warning}")
    if validate_context.exists():
        print(f"Validation helper:  {validate_context}")
    if run_verification.exists():
        print(f"Verification helper: {run_verification}")
    print("")
    print("Validation commands to run:")
    print("  python scripts/validate_context.py")
    print("  python scripts/run_verification.py --tier fast")
    print("")
    print(f"Overall: {'WARNINGS (see above)' if warnings_present else 'OK'}")
    return 0


def handle_recent_commits(repo_root: Path, count: int) -> int:
    commits = collect_recent_commits(repo_root, count=max(count, 1))
    coverage: dict[str, int] = {}
    print_header("Recent Commits (prompt-aware)")
    for commit in commits:
        label = commit.prompt_prefix or "(no prefix)"
        coverage[label] = coverage.get(label, 0) + 1
        print(f"{commit.short_hash}  {commit.date_text}  {commit.subject}")
    print("")
    print("Prompt coverage:")
    for label, total in coverage.items():
        print(f"- {label}: {total} commit{'s' if total != 1 else ''}")
    return 0


def handle_log_quota(
    repo_root: Path,
    script_cmd: str,
    slug: str | None,
    assistant: str,
    used_pct_5h: float | None,
    reset_at_5h: str | None,
    used_pct_7d: float | None,
    reset_at_7d: str | None,
    session_status: str | None,
    notes: str | None,
) -> int:
    state = load_work_state(repo_root, slug=slug)
    if state is None:
        print_missing_project_guidance(script_cmd)
        return 1
    rate_limits = load_rate_limits(repo_root, slug=slug)
    assistants = rate_limits.setdefault("assistants", {})
    assistant_key = assistant.strip().lower()
    if assistant_key not in assistants:
        print(f"Unsupported assistant: {assistant}")
        return 1
    record = assistants[assistant_key]
    if used_pct_5h is not None:
        record["five_hour_used_pct"] = used_pct_5h
    if reset_at_5h is not None:
        record["five_hour_reset_at"] = reset_at_5h
    if used_pct_7d is not None:
        record["seven_day_used_pct"] = used_pct_7d
    if reset_at_7d is not None:
        record["seven_day_reset_at"] = reset_at_7d
    if session_status is not None:
        record["session_status"] = session_status
    if notes is not None:
        record["notes"] = notes
    record["last_checked_at"] = iso_now()
    record["source"] = "manual"
    save_rate_limits(repo_root, rate_limits, slug=slug)
    ready, policy_reason = quota_policy_result(rate_limits)
    state.setdefault("quota_state", {})
    state["quota_state"]["ready_for_next_prompt"] = ready
    state["quota_state"]["notes"] = policy_reason if notes is None else notes
    save_work_state(repo_root, state, slug=slug)
    print(f"Quota updated: {assistant_key}")
    print(f"5h used: {format_optional_pct(record.get('five_hour_used_pct'))}   reset: {record.get('five_hour_reset_at') or 'unknown'}")
    print(f"7d used: {format_optional_pct(record.get('seven_day_used_pct'))}   reset: {record.get('seven_day_reset_at') or 'unknown'}")
    print(f"Policy check: {'ready' if ready else f'not ready — {policy_reason}'}")
    print("RATE_LIMITS.json: updated")
    print("WORK_STATE.json: quota_state updated")
    return 0


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
    print_resume_guidance(repo_root, script_cmd, inspection.states)
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
    if args.command == "init-project":
        return handle_init_project(repo_root, slug=args.slug, force=args.force)
    if args.command == "next":
        return handle_next(repo_root, script_cmd, slug=args.slug)
    if args.command == "start":
        return handle_start(repo_root, slug=args.slug, prompt_file=args.prompt_file, assistant=args.assistant)
    if args.command == "pause":
        return handle_pause(repo_root, slug=args.slug, prompt_file=args.prompt_file, reason=args.reason)
    if args.command == "done":
        return handle_done(repo_root, slug=args.slug, prompt_file=args.prompt_file)
    if args.command == "verify":
        return handle_verify(repo_root, script_cmd, slug=args.slug)
    if args.command == "recent-commits":
        return handle_recent_commits(repo_root, count=args.count)
    if args.command == "log-quota":
        return handle_log_quota(
            repo_root,
            script_cmd,
            slug=args.slug,
            assistant=args.assistant,
            used_pct_5h=args.used_pct_5h,
            reset_at_5h=args.reset_at_5h,
            used_pct_7d=args.used_pct_7d,
            reset_at_7d=args.reset_at_7d,
            session_status=args.session_status,
            notes=args.notes,
        )
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
