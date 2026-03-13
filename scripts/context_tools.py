#!/usr/bin/env python3
"""Shared helpers for context metadata, example ranking, and repo signal analysis."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from manifest_tools import build_context_bundle, normalize_string_list, parse_manifest


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from verification.helpers import (  # noqa: E402
    EXAMPLE_SUPPORT_FILENAMES,
    confidence_score,
    load_registry,
    verification_score,
)


@dataclass(frozen=True)
class WeightedPath:
    """Resolved weight metadata for one repo path."""

    path: str
    weight: int
    tier: str
    reason: str


def normalize_repo_path(path: str) -> str:
    """Return a normalized repository-relative path."""

    return Path(path).as_posix().lstrip("./")


def load_json(path: Path) -> object:
    """Load JSON from disk."""

    return json.loads(path.read_text(encoding="utf-8"))


def load_context_weights(repo_root: Path) -> dict[str, object]:
    """Load context weighting metadata."""

    path = repo_root / "context/context-weights.json"
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return data


def _resolve_rule_match(path: str, rules: list[dict[str, object]]) -> dict[str, object] | None:
    """Return the best matching weight rule for a path."""

    normalized = normalize_repo_path(path)
    matched: dict[str, object] | None = None
    matched_prefix_length = -1

    for rule in rules:
        prefix = rule.get("prefix")
        if not isinstance(prefix, str) or not prefix:
            continue
        normalized_prefix = normalize_repo_path(prefix)
        if not normalized.startswith(normalized_prefix):
            continue
        if len(normalized_prefix) > matched_prefix_length:
            matched = rule
            matched_prefix_length = len(normalized_prefix)
    return matched


def describe_weight(repo_root: Path, path: str) -> WeightedPath:
    """Return weighting metadata for a repository-relative path."""

    weights = load_context_weights(repo_root)
    defaults = weights.get("defaults", {})
    rules = weights.get("rules", [])
    overrides = weights.get("overrides", {})

    if not isinstance(defaults, dict):
        raise ValueError("context/context-weights.json: 'defaults' must be an object")
    if not isinstance(rules, list):
        raise ValueError("context/context-weights.json: 'rules' must be a list")
    if not isinstance(overrides, dict):
        raise ValueError("context/context-weights.json: 'overrides' must be an object")

    normalized = normalize_repo_path(path)
    override = overrides.get(normalized)
    if isinstance(override, dict):
        return WeightedPath(
            path=normalized,
            weight=int(override.get("weight", defaults.get("weight", 50))),
            tier=str(override.get("tier", defaults.get("tier", "support"))),
            reason=str(override.get("reason", defaults.get("reason", "Fallback weight."))),
        )

    rule_dicts = [rule for rule in rules if isinstance(rule, dict)]
    rule = _resolve_rule_match(normalized, rule_dicts)
    if rule is not None:
        return WeightedPath(
            path=normalized,
            weight=int(rule.get("weight", defaults.get("weight", 50))),
            tier=str(rule.get("tier", defaults.get("tier", "support"))),
            reason=str(rule.get("reason", defaults.get("reason", "Fallback weight."))),
        )

    return WeightedPath(
        path=normalized,
        weight=int(defaults.get("weight", 50)),
        tier=str(defaults.get("tier", "support")),
        reason=str(defaults.get("reason", "Fallback weight.")),
    )


def load_example_catalog(repo_root: Path) -> dict[str, object]:
    """Load canonical example metadata."""

    path = repo_root / "examples/catalog.json"
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return data


def _registry_metadata_by_path(repo_root: Path) -> dict[str, dict[str, object]]:
    registry: dict[str, dict[str, object]] = {}
    for entry in load_registry():
        raw_path = entry.get("path")
        if isinstance(raw_path, str) and raw_path.strip():
            registry[normalize_repo_path(raw_path)] = entry
    return registry


def _match_score(values: list[str], desired: list[str], multiplier: int) -> int:
    """Return a weighted score for overlapping tags."""

    return len(set(values) & set(desired)) * multiplier


def rank_examples(
    repo_root: Path,
    *,
    workflow_names: list[str] | None = None,
    stack_names: list[str] | None = None,
    archetype_names: list[str] | None = None,
    pattern_names: list[str] | None = None,
    preferred_paths: list[str] | None = None,
    limit: int = 5,
) -> list[dict[str, object]]:
    """Return the strongest canonical examples for the supplied filters."""

    workflow_names = workflow_names or []
    stack_names = stack_names or []
    archetype_names = archetype_names or []
    pattern_names = pattern_names or []
    preferred_paths = [normalize_repo_path(path) for path in (preferred_paths or [])]

    catalog = load_example_catalog(repo_root)
    entries = catalog.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("examples/catalog.json: 'entries' must be a list")

    registry = _registry_metadata_by_path(repo_root)
    ranked: list[dict[str, object]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue

        normalized_path = normalize_repo_path(str(entry.get("path", "")))
        registry_entry = registry.get(normalized_path, {})
        stacks = normalize_string_list(entry.get("stacks"))
        archetypes = normalize_string_list(entry.get("archetypes"))
        workflows = normalize_string_list(entry.get("workflows"))
        patterns = normalize_string_list(entry.get("patterns"))
        score = int(entry.get("rank", 0))
        score += _match_score(stacks, stack_names, 30)
        score += _match_score(archetypes, archetype_names, 20)
        score += _match_score(workflows, workflow_names, 18)
        score += _match_score(patterns, pattern_names, 8)
        if normalized_path in preferred_paths:
            score += 40
        score += verification_score(registry_entry) * 12
        score += confidence_score(registry_entry) * 4
        if stack_names and not set(stacks) & set(stack_names):
            score -= 5
        if archetype_names and not set(archetypes) & set(archetype_names):
            score -= 3
        if workflow_names and not set(workflows) & set(workflow_names):
            score -= 3
        ranked.append(
            {
                **entry,
                "score": score,
                "verification_level": registry_entry.get("verification_level", "untracked"),
                "confidence": registry_entry.get("confidence", "untracked"),
                "scenario_harness": registry_entry.get("scenario_harness", ""),
                "verification_targets": registry_entry.get("verification_targets", []),
            }
        )

    ranked.sort(key=lambda item: (-int(item["score"]), str(item.get("path", ""))))
    return ranked[:limit]


def load_repo_signal_hints(repo_root: Path) -> dict[str, object]:
    """Load repo signal hints metadata."""

    path = repo_root / "context/router/repo-signal-hints.json"
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level JSON value must be an object")
    return data


def _matching_patterns(target_root: Path, patterns: list[str]) -> list[str]:
    """Return the subset of patterns that match at least one file."""

    matches: list[str] = []
    for pattern in patterns:
        if not pattern:
            continue
        if any(path.is_file() for path in target_root.glob(pattern)):
            matches.append(pattern)
    return matches


def analyze_repo_signals(repo_root: Path, target_root: Path) -> dict[str, list[dict[str, object]]]:
    """Infer likely stacks, archetypes, workflows, and manifests for a repo."""

    hints = load_repo_signal_hints(repo_root)

    def rank_hint_group(group_name: str) -> list[dict[str, object]]:
        group = hints.get(group_name, [])
        if not isinstance(group, list):
            raise ValueError(f"context/router/repo-signal-hints.json: '{group_name}' must be a list")
        ranked: list[dict[str, object]] = []
        for entry in group:
            if not isinstance(entry, dict):
                continue
            patterns = normalize_string_list(entry.get("patterns"))
            matched = _matching_patterns(target_root, patterns)
            if not matched:
                continue
            ranked.append(
                {
                    "name": str(entry.get("name", "")),
                    "score": len(matched),
                    "matched_patterns": matched,
                    "guidance": str(entry.get("guidance", "")),
                }
            )
        ranked.sort(key=lambda item: (-int(item["score"]), str(item["name"])))
        return ranked

    manifests_dir = repo_root / "manifests"
    manifest_rankings: list[dict[str, object]] = []
    for manifest_path in sorted(manifests_dir.glob("*.yaml")):
        manifest_data = parse_manifest(manifest_path)
        signals = normalize_string_list(manifest_data.get("repo_signals"))
        matched = _matching_patterns(target_root, signals)
        if not matched:
            continue
        bundle = build_context_bundle(manifest_path, manifest_data, repo_root)
        manifest_rankings.append(
            {
                "name": manifest_path.stem,
                "score": len(matched),
                "matched_patterns": matched,
                "primary_stack": str(manifest_data.get("primary_stack", "")),
                "archetype": str(manifest_data.get("archetype", "")),
                "bundle_preview": bundle[:5],
            }
        )
    manifest_rankings.sort(key=lambda item: (-int(item["score"]), str(item["name"])))

    return {
        "stacks": rank_hint_group("stacks"),
        "archetypes": rank_hint_group("archetypes"),
        "workflows": rank_hint_group("workflows"),
        "manifests": manifest_rankings,
    }


def validate_context_weights(repo_root: Path) -> list[str]:
    """Validate the context weighting metadata."""

    errors: list[str] = []
    path = repo_root / "context/context-weights.json"
    data = load_context_weights(repo_root)
    defaults = data.get("defaults")
    rules = data.get("rules")
    overrides = data.get("overrides")

    if not isinstance(defaults, dict):
        return [f"{path}: 'defaults' must be an object"]
    if not isinstance(rules, list):
        errors.append(f"{path}: 'rules' must be a list")
    if not isinstance(overrides, dict):
        errors.append(f"{path}: 'overrides' must be an object")

    if isinstance(rules, list):
        for index, rule in enumerate(rules, start=1):
            if not isinstance(rule, dict):
                errors.append(f"{path}: rules[{index}] must be an object")
                continue
            prefix = rule.get("prefix")
            if not isinstance(prefix, str) or not prefix.strip():
                errors.append(f"{path}: rules[{index}] missing a non-empty 'prefix'")
                continue
            normalized = normalize_repo_path(prefix)
            if normalized.endswith("/"):
                if not (repo_root / normalized.rstrip("/")).exists():
                    errors.append(f"{path}: rules[{index}] prefix directory '{normalized}' does not exist")
            elif "*" not in normalized and not (repo_root / normalized).exists():
                errors.append(f"{path}: rules[{index}] prefix path '{normalized}' does not exist")

    if isinstance(overrides, dict):
        for override_path, value in overrides.items():
            normalized = normalize_repo_path(override_path)
            if not (repo_root / normalized).exists():
                errors.append(f"{path}: override path '{normalized}' does not exist")
            if not isinstance(value, dict):
                errors.append(f"{path}: override '{normalized}' must be an object")

    return errors


def validate_example_catalog(repo_root: Path) -> list[str]:
    """Validate the canonical example catalog."""

    errors: list[str] = []
    path = repo_root / "examples/catalog.json"
    data = load_example_catalog(repo_root)
    entries = data.get("entries")
    if not isinstance(entries, list):
        return [f"{path}: 'entries' must be a list"]

    registry = _registry_metadata_by_path(repo_root)
    seen_paths: set[str] = set()
    cataloged_paths: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"{path}: entries[{index}] must be an object")
            continue
        entry_path = entry.get("path")
        if not isinstance(entry_path, str) or not entry_path.strip():
            errors.append(f"{path}: entries[{index}] missing a non-empty 'path'")
            continue
        normalized = normalize_repo_path(entry_path)
        if normalized in seen_paths:
            errors.append(f"{path}: duplicate example path '{normalized}'")
        seen_paths.add(normalized)
        cataloged_paths.add(normalized)
        if not (repo_root / normalized).exists():
            errors.append(f"{path}: referenced example path does not exist: '{normalized}'")
        if normalized not in registry:
            errors.append(f"{path}: catalog path missing verification registry entry: '{normalized}'")
        for key in ("category", "summary", "stability"):
            value = entry.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{path}: entries[{index}] key '{key}' must be a non-empty string")
        for key in ("stacks", "archetypes", "workflows", "patterns"):
            if not isinstance(entry.get(key), list):
                errors.append(f"{path}: entries[{index}] key '{key}' must be a list")

    actual_example_paths = {
        normalize_repo_path(example_path.relative_to(repo_root).as_posix())
        for example_path in (repo_root / "examples").rglob("*")
        if example_path.is_file() and example_path.name not in EXAMPLE_SUPPORT_FILENAMES
    }
    missing = sorted(actual_example_paths - cataloged_paths)
    for missing_path in missing:
        errors.append(f"{path}: example file missing catalog entry: '{missing_path}'")
    return errors


def validate_repo_signal_hints(repo_root: Path) -> list[str]:
    """Validate repo signal hint metadata."""

    errors: list[str] = []
    path = repo_root / "context/router/repo-signal-hints.json"
    data = load_repo_signal_hints(repo_root)
    for key in ("stacks", "archetypes", "workflows", "extension_paths"):
        value = data.get(key)
        if not isinstance(value, list):
            errors.append(f"{path}: '{key}' must be a list")
            continue
        for index, entry in enumerate(value, start=1):
            if not isinstance(entry, dict):
                errors.append(f"{path}: {key}[{index}] must be an object")
                continue
            name = entry.get("name")
            guidance = entry.get("guidance")
            patterns = entry.get("patterns")
            if not isinstance(name, str) or not name.strip():
                errors.append(f"{path}: {key}[{index}] missing a non-empty 'name'")
            if not isinstance(guidance, str) or not guidance.strip():
                errors.append(f"{path}: {key}[{index}] missing a non-empty 'guidance'")
            if not isinstance(patterns, list) or not all(
                isinstance(pattern, str) and pattern.strip() for pattern in patterns
            ):
                errors.append(f"{path}: {key}[{index}] 'patterns' must be a list of strings")
    return errors


def validate_prompt_numbering(repo_root: Path) -> list[str]:
    """Validate monotonic prompt numbering for canonical prompt assets."""

    errors: list[str] = []
    directories = [
        repo_root / "examples/canonical-prompts",
        repo_root / "templates/prompt-first",
    ]
    for directory in directories:
        numbered_files = sorted(
            path.name for path in directory.glob("[0-9][0-9][0-9]-*.txt") if path.is_file()
        )
        observed = [int(name.split("-", 1)[0]) for name in numbered_files]
        expected = list(range(1, len(observed) + 1))
        if observed != expected:
            errors.append(
                f"{directory.relative_to(repo_root).as_posix()}: prompt numbering must be monotonic starting at 001"
            )
    return errors


def anchor_files(repo_root: Path) -> list[str]:
    """Return available assistant memory anchors."""

    anchors_dir = repo_root / "context/anchors"
    return sorted(
        path.relative_to(repo_root).as_posix()
        for path in anchors_dir.glob("*.md")
        if path.name != "README.md"
    )
