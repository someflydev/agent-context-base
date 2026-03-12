#!/usr/bin/env python3
"""Validate the v1 manifest files for presence and basic schema correctness."""

from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_KEYS = {
    "name",
    "archetype",
    "stacks",
    "triggers",
    "required_context",
    "optional_context",
    "preferred_examples",
    "warnings",
}

LIST_KEYS = {
    "stacks",
    "triggers",
    "required_context",
    "optional_context",
    "preferred_examples",
    "warnings",
}

ARCHETYPE_PATHS = {
    "prompt-first-repo": "context/archetypes/prompt-first-repo.md",
    "backend-api-service": "context/archetypes/backend-api-service.md",
    "cli-tool": "context/archetypes/cli-tool.md",
    "data-pipeline": "context/archetypes/data-pipeline.md",
    "local-rag-system": "context/archetypes/local-rag-system.md",
    "multi-storage-experiment": "context/archetypes/multi-storage-experiment.md",
    "polyglot-lab": "context/archetypes/polyglot-lab.md",
    "dokku-deployable-service": "context/archetypes/dokku-deployable-service.md",
}

STACK_PATHS = {
    "python-fastapi-uv-ruff-orjson-polars": "context/stacks/python-fastapi-uv-ruff-orjson-polars.md",
    "typescript-hono-bun": "context/stacks/typescript-hono-bun.md",
    "rust-axum-modern": "context/stacks/rust-axum-modern.md",
    "go-echo": "context/stacks/go-echo.md",
    "elixir-phoenix": "context/stacks/elixir-phoenix.md",
    "redis-keydb-mongo": "context/stacks/redis-keydb-mongo.md",
    "duckdb-trino-polars": "context/stacks/duckdb-trino-polars.md",
    "nats-jetstream": "context/stacks/nats-jetstream.md",
    "meilisearch": "context/stacks/meilisearch.md",
    "timescaledb": "context/stacks/timescaledb.md",
    "elasticsearch": "context/stacks/elasticsearch.md",
    "qdrant": "context/stacks/qdrant.md",
    "dokku-conventions": "context/stacks/dokku-conventions.md",
    "prompt-first-repo": "context/stacks/prompt-first-repo.md",
}


def parse_manifest(path: Path) -> dict[str, object]:
    """Parse a limited YAML subset used by the manifests in this repo."""

    data: dict[str, object] = {}
    current_list_key: str | None = None

    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- "):
            if current_list_key is None:
                raise ValueError(f"{path}:{lineno}: list item without an active list key")
            value = stripped[2:].strip()
            if not value:
                raise ValueError(f"{path}:{lineno}: empty list item")
            data[current_list_key].append(value)  # type: ignore[index]
            continue

        current_list_key = None
        if ":" not in stripped:
            raise ValueError(f"{path}:{lineno}: expected 'key: value' or list key")

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"{path}:{lineno}: empty key")

        if not value:
            if key not in LIST_KEYS:
                raise ValueError(f"{path}:{lineno}: non-list key '{key}' missing a value")
            data[key] = []
            current_list_key = key
            continue

        data[key] = value

    return data


def validate_manifest(repo_root: Path, manifest_path: Path) -> list[str]:
    """Return a list of validation errors for one manifest."""

    errors: list[str] = []
    try:
        data = parse_manifest(manifest_path)
    except ValueError as exc:
        return [str(exc)]

    missing = sorted(REQUIRED_KEYS - data.keys())
    for key in missing:
        errors.append(f"{manifest_path}: missing required key '{key}'")

    unexpected = sorted(set(data.keys()) - REQUIRED_KEYS)
    for key in unexpected:
        errors.append(f"{manifest_path}: unexpected key '{key}'")

    name = data.get("name")
    if isinstance(name, str):
        expected_name = manifest_path.stem
        if name != expected_name:
            errors.append(
                f"{manifest_path}: name '{name}' does not match filename stem '{expected_name}'"
            )
    else:
        errors.append(f"{manifest_path}: 'name' must be a string")

    archetype = data.get("archetype")
    if isinstance(archetype, str):
        archetype_path = ARCHETYPE_PATHS.get(archetype)
        if archetype_path is None:
            errors.append(f"{manifest_path}: unknown archetype '{archetype}'")
        elif not (repo_root / archetype_path).exists():
            errors.append(f"{manifest_path}: missing archetype file '{archetype_path}'")
    else:
        errors.append(f"{manifest_path}: 'archetype' must be a string")

    for list_key in LIST_KEYS:
        value = data.get(list_key)
        if not isinstance(value, list):
            errors.append(f"{manifest_path}: '{list_key}' must be a list")
            continue
        if not value:
            errors.append(f"{manifest_path}: '{list_key}' must not be empty")
            continue
        for item in value:
            if not isinstance(item, str) or not item.strip():
                errors.append(f"{manifest_path}: '{list_key}' contains a blank item")

    stacks = data.get("stacks")
    if isinstance(stacks, list):
        for stack in stacks:
            stack_path = STACK_PATHS.get(stack)
            if stack_path is None:
                errors.append(f"{manifest_path}: unknown stack '{stack}'")
            elif not (repo_root / stack_path).exists():
                errors.append(f"{manifest_path}: missing stack file '{stack_path}'")

    for ref_key in ("required_context", "optional_context", "preferred_examples"):
        refs = data.get(ref_key)
        if isinstance(refs, list):
            for ref in refs:
                if not (repo_root / ref).exists():
                    errors.append(f"{manifest_path}: referenced file does not exist: '{ref}'")

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    manifest_dir = repo_root / "manifests"
    manifest_paths = sorted(manifest_dir.glob("*.yaml"))

    if not manifest_paths:
        print("No manifest files found under manifests/.", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for manifest_path in manifest_paths:
        all_errors.extend(validate_manifest(repo_root, manifest_path))

    if all_errors:
        print("Manifest validation failed:", file=sys.stderr)
        for error in all_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(manifest_paths)} manifest files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

