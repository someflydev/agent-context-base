from __future__ import annotations

import math
import warnings
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


BASE_COSTS: dict[str, int] = {
    "anchor": 1,
    "manifest": 2,
    "doctrine": 3,
    "workflow": 3,
    "stack_pack": 4,
    "archetype_pack": 4,
    "canonical_example": 4,
    "large_example": 7,
    "validation_script_reference": 2,
    "deployment_doctrine": 4,
}


@dataclass
class ModifierContext:
    primary_stack: str | None = None
    primary_archetype: str | None = None
    active_workflow: str | None = None
    required_files: tuple[str, ...] = ()
    preferred_example: str | None = None
    deployment_trigger: bool = False
    secondary_stacks: tuple[str, ...] = ()
    declared_primary_example: str | None = None


@dataclass
class ArtifactScore:
    path: str
    artifact_type: str
    base_cost: int
    size_cost: int
    modifier_cost: int
    total_cost: int
    modifier_notes: tuple[str, ...]


@dataclass
class BundleScore:
    artifacts: tuple[ArtifactScore, ...]
    subtotal: int
    diversity_penalty: int
    ambiguity_penalty: int
    confidence_penalty: int
    change_surface_penalty: int
    total: int
    distinct_concept_tags: int
    stack_count: int
    archetype_count: int
    workflow_count: int
    example_count: int
    large_example_count: int


@dataclass(frozen=True)
class BudgetProfile:
    name: str
    max_points: int
    max_files: int
    max_stacks: int
    max_archetypes: int
    max_workflows: int
    max_examples: int
    max_large_examples: int


PROFILES: tuple[BudgetProfile, ...] = (
    BudgetProfile("tiny", 9, 4, 1, 1, 1, 0, 0),
    BudgetProfile("small", 15, 6, 1, 1, 1, 1, 0),
    BudgetProfile("medium", 22, 8, 2, 1, 2, 1, 1),
    BudgetProfile("large", 32, 10, 2, 2, 2, 2, 1),
    BudgetProfile("cross-system", 45, 14, 3, 2, 3, 2, 1),
)


def _normalize_path(path: str | Path) -> str:
    return str(path).replace("\\", "/")


def _strip_relative_prefix(path: str) -> str:
    normalized = _normalize_path(path)
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _path_parts(path: str) -> tuple[str, ...]:
    normalized = _strip_relative_prefix(path).strip("/")
    if not normalized:
        return ()
    return PurePosixPath(normalized).parts


def _path_has_prefix(path: str, prefix: tuple[str, ...]) -> bool:
    parts = _path_parts(path)
    for index in range(0, len(parts) - len(prefix) + 1):
        if parts[index : index + len(prefix)] == prefix:
            return True
    return False


def _path_basename(path: str) -> str:
    return PurePosixPath(_normalize_path(path)).name


def _path_stem(path: str) -> str:
    return PurePosixPath(_normalize_path(path)).stem


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _is_examples_path(path: str) -> bool:
    return _path_has_prefix(path, ("examples",))


def infer_artifact_type(path: str) -> str:
    normalized = _strip_relative_prefix(path)
    basename = _path_basename(normalized)
    suffix = PurePosixPath(normalized).suffix.lower()

    if _path_has_prefix(normalized, ("manifests",)) and suffix == ".yaml":
        artifact_type = "manifest"
    elif _path_has_prefix(normalized, ("context", "doctrine")) and suffix == ".md":
        artifact_type = "doctrine"
    elif _path_has_prefix(normalized, ("context", "workflows")) and suffix == ".md":
        artifact_type = "workflow"
    elif _path_has_prefix(normalized, ("context", "stacks")) and suffix == ".md":
        artifact_type = "stack_pack"
    elif _path_has_prefix(normalized, ("context", "archetypes")) and suffix == ".md":
        artifact_type = "archetype_pack"
    elif _path_has_prefix(normalized, ("context", "router")) and suffix in {".md", ".yaml", ".json"}:
        artifact_type = "anchor"
    elif _is_examples_path(normalized):
        path_obj = Path(path)
        is_large = path_obj.exists() and path_obj.is_file() and path_obj.stat().st_size > 8 * 1024
        artifact_type = "large_example" if is_large else "canonical_example"
    elif _path_has_prefix(normalized, ("verification",)):
        artifact_type = "validation_script_reference"
    elif _path_has_prefix(normalized, (".acb", "specs")) and suffix == ".md":
        artifact_type = "doctrine"
    elif basename in {"AGENT.md", "CLAUDE.md"}:
        artifact_type = "anchor"
    elif normalized == "README.md":
        artifact_type = "anchor"
    elif normalized in {"context/MEMORY.md", "context/TASK.md", "context/SESSION.md", "PLAN.md"}:
        artifact_type = "anchor"
    elif _path_has_prefix(normalized, ("docs", "usage")) and basename.startswith("SPEC_DRIVEN") and suffix == ".md":
        artifact_type = "doctrine"
    elif _path_has_prefix(normalized, ("docs",)) and suffix == ".md":
        artifact_type = "doctrine"
    elif suffix == ".md":
        artifact_type = "doctrine"
    else:
        artifact_type = "anchor"

    lowered = normalized.lower()
    if artifact_type == "doctrine" and ("dokku" in lowered or "deploy" in lowered):
        return "deployment_doctrine"
    return artifact_type


def _size_cost_for_path(path: Path) -> int:
    if not path.exists():
        warnings.warn(f"Missing file for context budget scoring: {path}", stacklevel=2)
        return 0
    estimated_tokens = math.ceil(path.stat().st_size / 4)
    return min(4, max(0, math.ceil(estimated_tokens / 400) - 1))


def classify_concept_tag(path: str) -> str:
    lowered = _normalize_path(path).lower()
    if "storage" in lowered or "database" in lowered:
        return "storage"
    if "deploy" in lowered or "dokku" in lowered:
        return "deployment"
    if "workflow" in lowered or "smoke" in lowered or "test" in lowered:
        return "verification"
    if "stack" in lowered:
        return "stack"
    if "rag" in lowered or "vector" in lowered or "search" in lowered:
        return "search"
    if "prompt" in lowered or "memory" in lowered or "session" in lowered:
        return "session-management"
    return "general"


def collect_concept_tags(paths: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for path in paths:
        tag = classify_concept_tag(path)
        if tag in seen:
            continue
        seen.add(tag)
        ordered.append(tag)
    return tuple(ordered)


def _matches_declared_file(path: str, declared_path: str | None) -> bool:
    if not declared_path:
        return False
    return _strip_relative_prefix(path) == _strip_relative_prefix(declared_path)


def _modifier_entries(path: str, artifact_type: str, ctx: ModifierContext | None) -> tuple[tuple[int, str], ...]:
    if ctx is None:
        return ()
    entries: list[tuple[int, str]] = []
    normalized = _strip_relative_prefix(path)
    stem = _path_stem(normalized)

    if artifact_type == "workflow" and ctx.active_workflow:
        if stem == ctx.active_workflow:
            entries.append((-1, "direct match"))
        else:
            entries.append((2, "cross domain"))

    if artifact_type == "stack_pack":
        if ctx.primary_stack and stem == ctx.primary_stack:
            entries.append((-1, "direct match"))
        elif ctx.secondary_stacks:
            try:
                index = ctx.secondary_stacks.index(stem)
            except ValueError:
                if ctx.primary_stack:
                    entries.append((2, "cross domain"))
            else:
                if index == 0:
                    entries.append((2, "secondary stack"))
                else:
                    entries.append((4, "third stack"))

    if artifact_type == "archetype_pack" and ctx.primary_archetype:
        if stem == ctx.primary_archetype:
            entries.append((-1, "direct match"))
        else:
            entries.append((3, "extra archetype"))

    if artifact_type in {"canonical_example", "large_example"} and _matches_declared_file(normalized, ctx.preferred_example):
        entries.append((-1, "preferred example"))

    if normalized in {_strip_relative_prefix(item) for item in ctx.required_files}:
        entries.append((-1, "required context"))

    if artifact_type == "deployment_doctrine" and not ctx.deployment_trigger:
        entries.append((4, "deployment without trigger"))

    if artifact_type == "large_example" and not _matches_declared_file(normalized, ctx.declared_primary_example):
        entries.append((2, "non-primary large example"))

    return tuple(entries)


def compute_modifiers(path: str, artifact_type: str, ctx: ModifierContext) -> int:
    return sum(cost for cost, _note in _modifier_entries(path, artifact_type, ctx))


def _score_artifact(path: Path, repo_root: Path, ctx: ModifierContext | None) -> ArtifactScore:
    display_path = _display_path(path, repo_root)
    artifact_type = infer_artifact_type(display_path)
    base_cost = BASE_COSTS[artifact_type]
    size_cost = _size_cost_for_path(path)
    modifier_entries = _modifier_entries(display_path, artifact_type, ctx)
    modifier_cost = sum(cost for cost, _note in modifier_entries)
    return ArtifactScore(
        path=display_path,
        artifact_type=artifact_type,
        base_cost=base_cost,
        size_cost=size_cost,
        modifier_cost=modifier_cost,
        total_cost=base_cost + size_cost + modifier_cost,
        modifier_notes=tuple(note for _cost, note in modifier_entries),
    )


def _resolve_input_path(raw_path: str, repo_root: Path) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return repo_root / candidate


def _confidence_penalty(confidence: float) -> int:
    if confidence >= 0.85:
        return 0
    if confidence >= 0.70:
        return 2
    return 4


def _change_surface_penalty(change_surface_area: int) -> int:
    return max(0, change_surface_area - 1)


def check_hard_caps(bundle_score: BundleScore, profile: BudgetProfile) -> list[str]:
    violations: list[str] = []
    if bundle_score.total > profile.max_points:
        violations.append(f"total {bundle_score.total} exceeds max_points {profile.max_points}")
    if len(bundle_score.artifacts) > profile.max_files:
        violations.append(f"files {len(bundle_score.artifacts)} exceeds max_files {profile.max_files}")
    if bundle_score.stack_count > profile.max_stacks:
        violations.append(f"stacks {bundle_score.stack_count} exceeds max_stacks {profile.max_stacks}")
    if bundle_score.archetype_count > profile.max_archetypes:
        violations.append(f"archetypes {bundle_score.archetype_count} exceeds max_archetypes {profile.max_archetypes}")
    if bundle_score.workflow_count > profile.max_workflows:
        violations.append(f"workflows {bundle_score.workflow_count} exceeds max_workflows {profile.max_workflows}")
    if bundle_score.example_count > profile.max_examples:
        violations.append(f"examples {bundle_score.example_count} exceeds max_examples {profile.max_examples}")
    if bundle_score.large_example_count > profile.max_large_examples:
        violations.append(
            f"large_examples {bundle_score.large_example_count} exceeds max_large_examples {profile.max_large_examples}"
        )
    if any("deployment without trigger" in artifact.modifier_notes for artifact in bundle_score.artifacts):
        violations.append("deployment docs require an explicit deployment trigger")
    validation_refs = len(
        [artifact for artifact in bundle_score.artifacts if artifact.artifact_type == "validation_script_reference"]
    )
    if validation_refs > 1:
        violations.append("validation_script_reference count exceeds hard cap 1")
    return violations


def select_profile(bundle_score: BundleScore) -> BudgetProfile | None:
    for profile in PROFILES:
        if not check_hard_caps(bundle_score, profile):
            return profile
    return None


def score_bundle(
    paths: list[str],
    repo_root: Path,
    ctx: ModifierContext | None = None,
    ambiguity_level: int = 0,
    confidence: float = 1.0,
    change_surface_area: int = 1,
) -> tuple[BundleScore, BudgetProfile | None, list[str]]:
    resolved_ctx = ctx
    artifacts = tuple(
        _score_artifact(_resolve_input_path(raw_path, repo_root), repo_root, resolved_ctx)
        for raw_path in paths
    )
    subtotal = sum(artifact.total_cost for artifact in artifacts)
    concept_tags = collect_concept_tags([artifact.path for artifact in artifacts])
    diversity_penalty = max(0, len(concept_tags) - 4)
    ambiguity_penalty = max(0, 2 * ambiguity_level)
    confidence_penalty = _confidence_penalty(confidence)
    change_surface_penalty = _change_surface_penalty(change_surface_area)
    bundle_score = BundleScore(
        artifacts=artifacts,
        subtotal=subtotal,
        diversity_penalty=diversity_penalty,
        ambiguity_penalty=ambiguity_penalty,
        confidence_penalty=confidence_penalty,
        change_surface_penalty=change_surface_penalty,
        total=subtotal + diversity_penalty + ambiguity_penalty + confidence_penalty + change_surface_penalty,
        distinct_concept_tags=len(concept_tags),
        stack_count=len([artifact for artifact in artifacts if artifact.artifact_type == "stack_pack"]),
        archetype_count=len([artifact for artifact in artifacts if artifact.artifact_type == "archetype_pack"]),
        workflow_count=len([artifact for artifact in artifacts if artifact.artifact_type == "workflow"]),
        example_count=len(
            [artifact for artifact in artifacts if artifact.artifact_type in {"canonical_example", "large_example"}]
        ),
        large_example_count=len([artifact for artifact in artifacts if artifact.artifact_type == "large_example"]),
    )
    selected_profile = select_profile(bundle_score)
    comparison_profile = selected_profile or PROFILES[-1]
    cap_violations = check_hard_caps(bundle_score, comparison_profile)
    return bundle_score, selected_profile, cap_violations
