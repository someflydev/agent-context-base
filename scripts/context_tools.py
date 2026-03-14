#!/usr/bin/env python3
"""Shared helpers for context metadata, example ranking, and repo signal analysis."""

from __future__ import annotations

import json
import re
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
    load_yaml_like,
    load_registry,
    registry_by_name,
    verification_score,
)


MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
MERMAID_BLOCK_PATTERN = re.compile(r"```mermaid\s*\n(.*?)```", flags=re.DOTALL)
MERMAID_PATH_PATTERN = re.compile(
    r"(?P<path>"
    r"README\.md|AGENT\.md|CLAUDE\.md|PROMPTS\.md|Procfile|app\.json|\.generated-profile\.yaml|"
    r"docker-compose(?:\.test)?\.yml|"
    r"(?:docs|context|manifests|examples|templates|scripts|verification|smoke-tests)/[A-Za-z0-9_./-]+"
    r")"
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


def validate_data_acquisition_consistency(repo_root: Path) -> list[str]:
    """Validate the polyglot data-acquisition index, matrix, and support posture."""

    errors: list[str] = []
    readme_path = repo_root / "examples/canonical-data-acquisition/README.md"
    matrix_path = repo_root / "examples/canonical-data-acquisition/language-support-matrix.yaml"
    invariant_path = repo_root / "context/doctrine/data-acquisition-invariants.md"
    if not invariant_path.exists():
        errors.append(f"{invariant_path}: missing invariant doc")
    if not readme_path.exists():
        errors.append(f"{readme_path}: missing canonical data-acquisition README")
        return errors
    if not matrix_path.exists():
        errors.append(f"{matrix_path}: missing language support matrix")
        return errors

    readme_text = readme_path.read_text(encoding="utf-8")
    for section in (
        "## Capability Gap",
        "## Invariant Layer",
        "## Language Matrix",
        "## Selection Contract",
        "## Verification Posture",
    ):
        if section not in readme_text:
            errors.append(f"{readme_path}: missing required section '{section}'")

    matrix = load_yaml_like(matrix_path)
    if not isinstance(matrix, dict):
        return [f"{matrix_path}: top-level value must be an object"]
    languages = matrix.get("languages", [])
    shared_examples = matrix.get("shared_examples", [])
    if not isinstance(languages, list):
        errors.append(f"{matrix_path}: 'languages' must be a list")
        languages = []
    if not isinstance(shared_examples, list):
        errors.append(f"{matrix_path}: 'shared_examples' must be a list")
        shared_examples = []

    known_examples = registry_by_name()
    for entry in shared_examples:
        if not isinstance(entry, dict):
            errors.append(f"{matrix_path}: shared_examples entries must be objects")
            continue
        name = str(entry.get("name", "")).strip()
        if name not in known_examples:
            errors.append(f"{matrix_path}: unknown shared example '{name}'")
            continue
        registry_entry = known_examples[name]
        if str(registry_entry.get("path", "")).strip() != str(entry.get("path", "")).strip():
            errors.append(f"{matrix_path}: shared example '{name}' path does not match registry")
        if str(registry_entry.get("verification_level", "")).strip() != str(
            entry.get("verification_level", "")
        ).strip():
            errors.append(f"{matrix_path}: shared example '{name}' verification level does not match registry")

    support_matrix = load_yaml_like(repo_root / "verification/stack_support_matrix.yaml")
    capabilities = support_matrix.get("capabilities", []) if isinstance(support_matrix, dict) else []
    capability = next(
        (
            entry
            for entry in capabilities
            if isinstance(entry, dict) and str(entry.get("capability", "")).strip() == "canonical-data-acquisition"
        ),
        None,
    )
    if capability is None:
        errors.append("verification/stack_support_matrix.yaml: missing canonical-data-acquisition capability block")
        capability_stacks = []
    else:
        capability_shared = capability.get("shared_examples", [])
        if capability_shared != [entry.get("name") for entry in shared_examples if isinstance(entry, dict)]:
            errors.append("verification/stack_support_matrix.yaml: shared example names do not match acquisition matrix")
        capability_stacks = capability.get("stacks", [])
        if not isinstance(capability_stacks, list):
            errors.append("verification/stack_support_matrix.yaml: capability stacks must be a list")
            capability_stacks = []

    capability_by_stack = {
        str(entry.get("stack", "")).strip(): entry
        for entry in capability_stacks
        if isinstance(entry, dict) and str(entry.get("stack", "")).strip()
    }

    for entry in languages:
        if not isinstance(entry, dict):
            errors.append(f"{matrix_path}: language rows must be objects")
            continue
        language = str(entry.get("language", "")).strip()
        stack = str(entry.get("stack", "")).strip()
        posture = str(entry.get("verification_posture", "")).strip()
        fallback_example = str(entry.get("fallback_example", "")).strip()
        fallback_path = str(entry.get("fallback_path", "")).strip()
        fallback_level = str(entry.get("fallback_verification_level", "")).strip()
        follow_on_prompt = str(entry.get("follow_on_prompt", "")).strip()

        expected_row = (
            f"| {language} | {stack} | none yet | {posture} | "
            f"{fallback_path} ({fallback_level}) | {follow_on_prompt} |"
        )
        if expected_row not in readme_text:
            errors.append(f"{readme_path}: missing matrix row '{expected_row}'")

        registry_entry = known_examples.get(fallback_example)
        if registry_entry is None:
            errors.append(f"{matrix_path}: fallback example '{fallback_example}' is missing from registry")
        else:
            if str(registry_entry.get("path", "")).strip() != fallback_path:
                errors.append(f"{matrix_path}: fallback path for '{fallback_example}' does not match registry")
            if str(registry_entry.get("verification_level", "")).strip() != fallback_level:
                errors.append(f"{matrix_path}: fallback level for '{fallback_example}' does not match registry")

        support_entry = capability_by_stack.get(stack)
        if support_entry is None:
            errors.append(f"verification/stack_support_matrix.yaml: missing acquisition capability entry for '{stack}'")
            continue
        if str(support_entry.get("status", "")).strip() != posture:
            errors.append(f"verification/stack_support_matrix.yaml: status mismatch for '{stack}'")
        if str(support_entry.get("fallback_example", "")).strip() != fallback_example:
            errors.append(f"verification/stack_support_matrix.yaml: fallback example mismatch for '{stack}'")
        if str(support_entry.get("fallback_verification_level", "")).strip() != fallback_level:
            errors.append(f"verification/stack_support_matrix.yaml: fallback level mismatch for '{stack}'")
        if str(support_entry.get("follow_on_prompt", "")).strip() != follow_on_prompt:
            errors.append(f"verification/stack_support_matrix.yaml: follow-on prompt mismatch for '{stack}'")

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


def _markdown_paths(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    root_readme = repo_root / "README.md"
    if root_readme.exists():
        paths.append(root_readme)

    for root_name in ("docs", "context", "examples", "templates", "scripts", "verification"):
        root = repo_root / root_name
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            if "verification/fixtures" in path.relative_to(repo_root).as_posix():
                continue
            paths.append(path)
    return sorted(set(paths))


def _resolve_markdown_target(repo_root: Path, doc_path: Path, target: str) -> Path | None:
    cleaned = target.split("#", 1)[0].split("?", 1)[0].strip()
    if not cleaned or cleaned.startswith(("http://", "https://", "mailto:")):
        return None
    return (doc_path.parent / cleaned).resolve()


def validate_markdown_cross_references(repo_root: Path) -> list[str]:
    """Validate relative markdown links used across docs."""

    errors: list[str] = []
    repo_root_resolved = repo_root.resolve()
    for doc_path in _markdown_paths(repo_root):
        text = doc_path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_PATTERN.finditer(text):
            target = match.group(1).strip()
            resolved = _resolve_markdown_target(repo_root, doc_path, target)
            if resolved is None:
                continue
            if repo_root_resolved not in resolved.parents and resolved != repo_root_resolved:
                errors.append(f"{doc_path.relative_to(repo_root).as_posix()}: link escapes repo: '{target}'")
                continue
            if not resolved.exists():
                errors.append(
                    f"{doc_path.relative_to(repo_root).as_posix()}: broken markdown link '{target}'"
                )
    return errors


def validate_mermaid_reference_hints(repo_root: Path) -> list[str]:
    """Validate obvious repo-path references inside Mermaid blocks."""

    errors: list[str] = []
    for doc_path in _markdown_paths(repo_root):
        text = doc_path.read_text(encoding="utf-8")
        relative_doc = doc_path.relative_to(repo_root).as_posix()
        for block in MERMAID_BLOCK_PATTERN.findall(text):
            seen: set[str] = set()
            for match in MERMAID_PATH_PATTERN.finditer(block):
                raw = match.group("path")
                if raw in seen:
                    continue
                seen.add(raw)
                candidate = repo_root / raw
                if not candidate.exists():
                    errors.append(f"{relative_doc}: Mermaid reference points to missing path '{raw}'")
    return errors


def anchor_files(repo_root: Path) -> list[str]:
    """Return available assistant memory anchors."""

    anchors_dir = repo_root / "context/anchors"
    return sorted(
        path.relative_to(repo_root).as_posix()
        for path in anchors_dir.glob("*.md")
        if path.name != "README.md"
    )
