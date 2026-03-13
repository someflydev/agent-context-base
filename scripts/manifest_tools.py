#!/usr/bin/env python3
"""Shared helpers for parsing, validating, and previewing repo manifests."""

from __future__ import annotations

from pathlib import Path


LIST_KEYS = {
    "secondary_stacks",
    "triggers",
    "aliases",
    "required_context",
    "optional_context",
    "preferred_examples",
    "recommended_templates",
    "repo_signals",
    "task_hints",
    "warnings",
    "bootstrap_defaults",
    "compose_files",
    "data_isolation",
    "smoke_test_expectations",
}

REQUIRED_KEYS = {
    "schema_version",
    "name",
    "description",
    "archetype",
    "primary_stack",
    "secondary_stacks",
    "triggers",
    "aliases",
    "required_context",
    "optional_context",
    "preferred_examples",
    "recommended_templates",
    "repo_signals",
    "task_hints",
    "warnings",
    "bootstrap_defaults",
    "compose_files",
    "compose_project_name_dev",
    "compose_project_name_test",
    "port_band_app_dev",
    "port_band_app_test",
    "port_band_data_dev",
    "port_band_data_test",
    "data_isolation",
    "dokku_relevance",
    "smoke_test_expectations",
    "prompt_first_support",
}

PATH_LIST_KEYS = {
    "required_context",
    "optional_context",
    "preferred_examples",
    "recommended_templates",
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
    "nim-jester-happyx": "context/stacks/nim-jester-happyx.md",
    "scala-tapir-http4s-zio": "context/stacks/scala-tapir-http4s-zio.md",
    "zig-zap-jetzig": "context/stacks/zig-zap-jetzig.md",
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

VALID_SUPPORT_LEVELS = {"first-class", "supported", "optional", "not-applicable"}


def parse_scalar(raw: str) -> object:
    """Parse the constrained scalar values used in manifest files."""

    value = raw.strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        return value[1:-1]
    if value.isdigit():
        return int(value)
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


def parse_port_band(raw: str) -> tuple[int, int]:
    """Parse a port band like 14000-14099."""

    start_raw, end_raw = raw.split("-", 1)
    start = int(start_raw)
    end = int(end_raw)
    if start > end:
        raise ValueError(f"invalid port band '{raw}': start must be <= end")
    return start, end


def parse_manifest(path: Path) -> dict[str, object]:
    """Parse the limited YAML subset used by manifests in this repo."""

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
            data[current_list_key].append(parse_scalar(value))  # type: ignore[index]
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

        data[key] = parse_scalar(value)

    return data


def resolve_manifest(repo_root: Path, raw: str) -> Path:
    """Resolve a manifest name or path into a concrete file path."""

    candidate = Path(raw)
    if candidate.is_absolute():
        path = candidate
    elif "/" in raw or raw.endswith(".yaml"):
        path = (repo_root / candidate).resolve()
    else:
        path = (repo_root / "manifests" / f"{raw}.yaml").resolve()

    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {raw}")
    return path


def normalize_string_list(value: object) -> list[str]:
    """Return a list of non-empty strings or an empty list."""

    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            result.append(item)
    return result


def build_context_bundle(manifest_path: Path, data: dict[str, object], repo_root: Path) -> list[str]:
    """Return the ordered context bundle for a manifest."""

    ordered_bundle = [
        "README.md",
        "docs/repo-purpose.md",
        "docs/repo-layout.md",
        manifest_path.relative_to(repo_root).as_posix(),
        *normalize_string_list(data.get("required_context")),
        *normalize_string_list(data.get("optional_context")),
        *normalize_string_list(data.get("preferred_examples")),
    ]

    seen: set[str] = set()
    deduped_bundle: list[str] = []
    for entry in ordered_bundle:
        if entry not in seen:
            seen.add(entry)
            deduped_bundle.append(entry)
    return deduped_bundle


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

    schema_version = data.get("schema_version")
    if schema_version != 2:
        errors.append(f"{manifest_path}: 'schema_version' must be 2")

    name = data.get("name")
    if isinstance(name, str):
        expected_name = manifest_path.stem
        if name != expected_name:
            errors.append(
                f"{manifest_path}: name '{name}' does not match filename stem '{expected_name}'"
            )
    else:
        errors.append(f"{manifest_path}: 'name' must be a string")

    for key in (
        "description",
        "compose_project_name_dev",
        "compose_project_name_test",
        "port_band_app_dev",
        "port_band_app_test",
        "port_band_data_dev",
        "port_band_data_test",
        "dokku_relevance",
        "prompt_first_support",
    ):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{manifest_path}: '{key}' must be a non-empty string")

    for key in LIST_KEYS:
        value = data.get(key)
        if not isinstance(value, list):
            errors.append(f"{manifest_path}: '{key}' must be a list")
            continue
        if not value:
            errors.append(f"{manifest_path}: '{key}' must not be empty")
            continue
        for item in value:
            if not isinstance(item, str) or not item.strip():
                errors.append(f"{manifest_path}: '{key}' contains a blank item")

    archetype = data.get("archetype")
    if isinstance(archetype, str):
        archetype_path = ARCHETYPE_PATHS.get(archetype)
        if archetype_path is None:
            errors.append(f"{manifest_path}: unknown archetype '{archetype}'")
        elif not (repo_root / archetype_path).exists():
            errors.append(f"{manifest_path}: missing archetype file '{archetype_path}'")
    else:
        errors.append(f"{manifest_path}: 'archetype' must be a string")

    primary_stack = data.get("primary_stack")
    if isinstance(primary_stack, str):
        stack_path = STACK_PATHS.get(primary_stack)
        if stack_path is None:
            errors.append(f"{manifest_path}: unknown primary stack '{primary_stack}'")
        elif not (repo_root / stack_path).exists():
            errors.append(f"{manifest_path}: missing stack file '{stack_path}'")
    else:
        errors.append(f"{manifest_path}: 'primary_stack' must be a string")

    for stack in normalize_string_list(data.get("secondary_stacks")):
        stack_path = STACK_PATHS.get(stack)
        if stack_path is None:
            errors.append(f"{manifest_path}: unknown secondary stack '{stack}'")
        elif not (repo_root / stack_path).exists():
            errors.append(f"{manifest_path}: missing stack file '{stack_path}'")

    for ref_key in PATH_LIST_KEYS:
        refs = normalize_string_list(data.get(ref_key))
        for ref in refs:
            if not (repo_root / ref).exists():
                errors.append(f"{manifest_path}: referenced file does not exist: '{ref}'")

    for key in ("dokku_relevance", "prompt_first_support"):
        value = data.get(key)
        if isinstance(value, str) and value not in VALID_SUPPORT_LEVELS:
            errors.append(
                f"{manifest_path}: '{key}' must be one of {sorted(VALID_SUPPORT_LEVELS)}"
            )

    compose_files = normalize_string_list(data.get("compose_files"))
    required_compose_files = {"docker-compose.yml", "docker-compose.test.yml"}
    if compose_files and not required_compose_files.issubset(set(compose_files)):
        errors.append(
            f"{manifest_path}: 'compose_files' must include {sorted(required_compose_files)}"
        )

    compose_project_name_dev = data.get("compose_project_name_dev")
    compose_project_name_test = data.get("compose_project_name_test")
    if isinstance(compose_project_name_dev, str) and "{repo_slug}" not in compose_project_name_dev:
        errors.append(f"{manifest_path}: 'compose_project_name_dev' should include '{{repo_slug}}'")
    if isinstance(compose_project_name_test, str):
        if "{repo_slug}" not in compose_project_name_test:
            errors.append(f"{manifest_path}: 'compose_project_name_test' should include '{{repo_slug}}'")
        if "-test" not in compose_project_name_test:
            errors.append(f"{manifest_path}: 'compose_project_name_test' should end with a '-test' variant")
    if (
        isinstance(compose_project_name_dev, str)
        and isinstance(compose_project_name_test, str)
        and compose_project_name_dev == compose_project_name_test
    ):
        errors.append(f"{manifest_path}: dev and test compose project names must differ")

    port_keys = (
        "port_band_app_dev",
        "port_band_app_test",
        "port_band_data_dev",
        "port_band_data_test",
    )
    port_ranges: dict[str, tuple[int, int]] = {}
    for key in port_keys:
        value = data.get(key)
        if isinstance(value, str):
            try:
                port_ranges[key] = parse_port_band(value)
            except ValueError as exc:
                errors.append(f"{manifest_path}: '{key}' {exc}")
    for left_index, left_key in enumerate(port_keys):
        left_range = port_ranges.get(left_key)
        if left_range is None:
            continue
        for right_key in port_keys[left_index + 1 :]:
            right_range = port_ranges.get(right_key)
            if right_range is None:
                continue
            if left_range[0] <= right_range[1] and right_range[0] <= left_range[1]:
                errors.append(
                    f"{manifest_path}: port bands '{left_key}' and '{right_key}' must not overlap"
                )

    data_isolation = normalize_string_list(data.get("data_isolation"))
    if data_isolation:
        if not any(item == "docker/volumes/dev" for item in data_isolation):
            errors.append(f"{manifest_path}: 'data_isolation' should include 'docker/volumes/dev'")
        if not any(item == "docker/volumes/test" for item in data_isolation):
            errors.append(f"{manifest_path}: 'data_isolation' should include 'docker/volumes/test'")

    return errors
