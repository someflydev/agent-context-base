#!/usr/bin/env python3
"""Bootstrap a new repo from the agent-context-base conventions.

Examples:
    python scripts/new_repo.py analytics-api \
        --archetype backend-api-service \
        --primary-stack python-fastapi-uv-ruff-orjson-polars \
        --smoke-tests \
        --integration-tests \
        --seed-data \
        --dokku

    python scripts/new_repo.py prompt-kit \
        --archetype prompt-first-repo \
        --primary-stack prompt-first-repo \
        --prompt-first \
        --target-dir /tmp/prompt-kit
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from manifest_tools import parse_manifest


@dataclass(frozen=True)
class StackProfile:
    description: str
    display_name: str
    app_image: str
    app_command: str
    test_command: str
    app_container_port: int
    route_path: str
    smoke_path: str
    integration_path: str
    seed_path: str
    directories: tuple[str, ...]
    stack_gitignore: tuple[str, ...]
    extra_template: str | None = None


ARCHETYPES = {
    "backend-api-service": "HTTP service with handlers, storage boundaries, and smoke tests.",
    "cli-tool": "Operator-facing command-line tool with explicit commands and outputs.",
    "data-pipeline": "Transform-heavy repo with deterministic data flow and small fixtures.",
    "local-rag-system": "Local retrieval/indexing repo with deterministic corpus and smoke queries.",
    "multi-storage-experiment": "Repo that compares multiple backing services intentionally.",
    "prompt-first-repo": "Prompt-driven repo foundation with explicit context and routing files.",
    "dokku-deployable-service": "Single deployable service with Dokku-oriented deployment notes.",
}

STACKS: dict[str, StackProfile] = {
    "python-fastapi-uv-ruff-orjson-polars": StackProfile(
        description="FastAPI service using uv, Ruff, orjson, and Polars.",
        display_name="FastAPI + uv + Ruff + orjson + Polars",
        app_image="python:3.12-slim",
        app_command='sh -lc "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"',
        test_command='sh -lc "pytest -q"',
        app_container_port=8000,
        route_path="app/api/reports.py",
        smoke_path="tests/smoke/test_health.py",
        integration_path="tests/integration/test_report_runs.py",
        seed_path="scripts/seed_data.py",
        directories=(
            "app",
            "app/api",
            "app/services",
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "tests/smoke",
            "tests/integration",
        ),
        stack_gitignore=(".coverage",),
    ),
    "typescript-hono-bun": StackProfile(
        description="Lightweight Hono service using Bun, Drizzle ORM, and TSX route files.",
        display_name="TypeScript + Hono + Bun + Drizzle ORM + TSX",
        app_image="oven/bun:1",
        app_command='sh -lc "bun install && bun run --hot src/index.ts"',
        test_command='sh -lc "bun test"',
        app_container_port=3000,
        route_path="src/routes/reports.tsx",
        smoke_path="tests/smoke/health.smoke.ts",
        integration_path="tests/integration/report-runs.int.ts",
        seed_path="scripts/seed-data.ts",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "src/db",
            "src/routes",
            "tests/smoke",
            "tests/integration",
        ),
        stack_gitignore=("*.tsbuildinfo",),
        extra_template="templates/typescript-hono-bun/README.template.md",
    ),
    "rust-axum-modern": StackProfile(
        description="Rust HTTP service using Axum.",
        display_name="Rust + Axum",
        app_image="rust:1.85-bookworm",
        app_command='sh -lc "cargo run"',
        test_command='sh -lc "cargo test"',
        app_container_port=3000,
        route_path="src/main.rs",
        smoke_path="tests/smoke_health.rs",
        integration_path="tests/report_runs_integration.rs",
        seed_path="scripts/seed_data.sql",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "src",
            "tests",
        ),
        stack_gitignore=(),
    ),
    "go-echo": StackProfile(
        description="Go HTTP service using Echo and templ.",
        display_name="Go + Echo + templ",
        app_image="golang:1.24-bookworm",
        app_command='sh -lc "go run ./cmd/server"',
        test_command='sh -lc "go test ./..."',
        app_container_port=8080,
        route_path="cmd/server/main.go",
        smoke_path="tests/smoke/health_test.go",
        integration_path="tests/integration/report_runs_test.go",
        seed_path="scripts/seed_data.sql",
        directories=(
            "cmd/server",
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "internal/http",
            "internal/views",
            "manifests",
            "scripts",
            "tests/smoke",
            "tests/integration",
        ),
        stack_gitignore=(),
    ),
    "elixir-phoenix": StackProfile(
        description="Phoenix web or API surface with explicit controller and router boundaries.",
        display_name="Elixir + Phoenix",
        app_image="hexpm/elixir:1.17.3-erlang-27.1-debian-bookworm-20240701-slim",
        app_command='sh -lc "mix phx.server"',
        test_command='sh -lc "mix test"',
        app_container_port=4000,
        route_path="lib/app_web/router.ex",
        smoke_path="test/app_web/controllers/health_controller_test.exs",
        integration_path="test/app/reporting_test.exs",
        seed_path="priv/repo/seeds.exs",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "lib",
            "manifests",
            "priv/repo",
            "scripts",
            "test",
        ),
        stack_gitignore=(".elixir_ls/", "erl_crash.dump"),
    ),
    "prompt-first-repo": StackProfile(
        description="Prompt-first repo surface for manifests, docs, and staged prompts.",
        display_name="Prompt-First Meta Repo",
        app_image="python:3.12-slim",
        app_command='sh -lc "python -m http.server 8000"',
        test_command='sh -lc "python scripts/validate_repo.py"',
        app_container_port=8000,
        route_path="README.md",
        smoke_path="scripts/check_repo.py",
        integration_path="scripts/check_generated_profile.py",
        seed_path="scripts/seed_data.py",
        directories=(
            ".prompts",
            "docs",
            "manifests",
            "scripts",
        ),
        stack_gitignore=(),
    ),
    "qdrant": StackProfile(
        description="Local RAG base using Qdrant with deterministic indexing metadata.",
        display_name="Local RAG + Qdrant",
        app_image="python:3.12-slim",
        app_command='sh -lc "python -m app.index_documents"',
        test_command='sh -lc "pytest -q"',
        app_container_port=8000,
        route_path="app/index_documents.py",
        smoke_path="tests/smoke/test_index_smoke.py",
        integration_path="tests/integration/test_qdrant_round_trip.py",
        seed_path="scripts/seed_data.py",
        directories=(
            "app",
            "data/corpus",
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "tests/smoke",
            "tests/integration",
        ),
        stack_gitignore=(".coverage",),
    ),
    "duckdb-trino-polars": StackProfile(
        description="Data pipeline base using DuckDB, Trino, and Polars.",
        display_name="DuckDB + Trino + Polars",
        app_image="python:3.12-slim",
        app_command='sh -lc "python -m app.pipeline"',
        test_command='sh -lc "pytest -q"',
        app_container_port=8000,
        route_path="app/pipeline.py",
        smoke_path="tests/smoke/test_pipeline_smoke.py",
        integration_path="tests/integration/test_pipeline_round_trip.py",
        seed_path="scripts/seed_data.py",
        directories=(
            "app",
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "tests/smoke",
            "tests/integration",
        ),
        stack_gitignore=(".coverage",),
    ),
    "redis-keydb-mongo": StackProfile(
        description="Multi-storage experimentation base for Redis, KeyDB, and MongoDB.",
        display_name="Redis or KeyDB + MongoDB",
        app_image="python:3.12-slim",
        app_command='sh -lc "python -m app.main"',
        test_command='sh -lc "pytest -q"',
        app_container_port=8000,
        route_path="app/main.py",
        smoke_path="tests/smoke/test_storage_smoke.py",
        integration_path="tests/integration/test_storage_round_trip.py",
        seed_path="scripts/seed_data.py",
        directories=(
            "app",
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "tests/smoke",
            "tests/integration",
        ),
        stack_gitignore=(".coverage",),
    ),
}

DEFAULT_MANIFESTS = {
    ("backend-api-service", "python-fastapi-uv-ruff-orjson-polars"): ["backend-api-fastapi-polars"],
    ("backend-api-service", "typescript-hono-bun"): ["backend-api-typescript-hono-bun"],
    ("backend-api-service", "rust-axum-modern"): ["backend-api-rust-axum"],
    ("backend-api-service", "go-echo"): ["backend-api-go-echo"],
    ("backend-api-service", "elixir-phoenix"): ["webapp-elixir-phoenix"],
    ("cli-tool", "python-fastapi-uv-ruff-orjson-polars"): ["cli-python"],
    ("data-pipeline", "duckdb-trino-polars"): ["data-pipeline-polars"],
    ("local-rag-system", "qdrant"): ["local-rag-base"],
    ("multi-storage-experiment", "redis-keydb-mongo"): ["multi-storage-zoo"],
    ("prompt-first-repo", "prompt-first-repo"): ["prompt-first-meta-repo"],
    ("dokku-deployable-service", "python-fastapi-uv-ruff-orjson-polars"): [
        "backend-api-fastapi-polars",
        "dokku-deployable-fastapi",
    ],
    ("dokku-deployable-service", "typescript-hono-bun"): [
        "backend-api-typescript-hono-bun",
        "dokku-deployable-typescript-hono-bun",
    ],
    ("dokku-deployable-service", "go-echo"): [
        "backend-api-go-echo",
        "dokku-deployable-go-echo",
    ],
    ("dokku-deployable-service", "elixir-phoenix"): [
        "webapp-elixir-phoenix",
        "dokku-deployable-phoenix",
    ],
}

DOKKU_MANIFESTS = {
    "python-fastapi-uv-ruff-orjson-polars": "dokku-deployable-fastapi",
    "typescript-hono-bun": "dokku-deployable-typescript-hono-bun",
    "go-echo": "dokku-deployable-go-echo",
    "elixir-phoenix": "dokku-deployable-phoenix",
}

SERVICE_PRESETS = {
    "postgres": {
        "image": "postgres:16-alpine",
        "container_port": 5432,
        "env": (
            "POSTGRES_DB=app",
            "POSTGRES_USER=app",
            "POSTGRES_PASSWORD=app",
        ),
        "volume_path": "/var/lib/postgresql/data",
    },
    "timescaledb": {
        "image": "timescale/timescaledb:2.17.2-pg16",
        "container_port": 5432,
        "env": (
            "POSTGRES_DB=app",
            "POSTGRES_USER=app",
            "POSTGRES_PASSWORD=app",
        ),
        "volume_path": "/var/lib/postgresql/data",
    },
    "redis": {
        "image": "redis:7-alpine",
        "container_port": 6379,
        "env": (),
        "volume_path": "/data",
    },
    "mongo": {
        "image": "mongo:7",
        "container_port": 27017,
        "env": (),
        "volume_path": "/data/db",
    },
    "meilisearch": {
        "image": "getmeili/meilisearch:v1.14",
        "container_port": 7700,
        "env": ("MEILI_ENV=development",),
        "volume_path": "/meili_data",
    },
    "elasticsearch": {
        "image": "docker.elastic.co/elasticsearch/elasticsearch:8.17.3",
        "container_port": 9200,
        "env": (
            "discovery.type=single-node",
            "xpack.security.enabled=false",
        ),
        "volume_path": "/usr/share/elasticsearch/data",
    },
    "qdrant": {
        "image": "qdrant/qdrant:v1.13.5",
        "container_port": 6333,
        "env": (),
        "volume_path": "/qdrant/storage",
    },
    "nats": {
        "image": "nats:2.10-alpine",
        "container_port": 4222,
        "env": (),
        "volume_path": "/data",
    },
    "trino": {
        "image": "trinodb/trino:457",
        "container_port": 8080,
        "env": (),
        "volume_path": "/data/trino",
    },
}


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_name", nargs="?", help="Name of the new repo")
    parser.add_argument("--target-dir", help="Directory to create. Defaults to ./<repo-name>")
    parser.add_argument("--archetype", choices=sorted(ARCHETYPES))
    parser.add_argument("--primary-stack", choices=sorted(STACKS))
    parser.add_argument(
        "--manifest",
        action="append",
        default=[],
        help="Manifest name to include. May be repeated.",
    )
    parser.add_argument("--dokku", action="store_true", help="Generate Dokku starter files.")
    parser.add_argument(
        "--prompt-first",
        action="store_true",
        help="Generate prompt directory starter files.",
    )
    parser.add_argument(
        "--smoke-tests",
        action="store_true",
        help="Generate a stack-aware smoke-test starter.",
    )
    parser.add_argument(
        "--integration-tests",
        action="store_true",
        help="Generate a stack-aware integration-test starter.",
    )
    parser.add_argument(
        "--seed-data",
        action="store_true",
        help="Generate a deterministic seed-data starter.",
    )
    parser.add_argument(
        "--docker-layout",
        action="store_true",
        help="Generate docker-compose.yml and docker-compose.test.yml even if not implied.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow writing into an existing non-empty target directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned files without writing them.",
    )
    parser.add_argument(
        "--no-profile",
        action="store_true",
        help="Skip writing .generated-profile.yaml.",
    )
    parser.add_argument(
        "--list-archetypes",
        action="store_true",
        help="Print supported archetypes and exit.",
    )
    parser.add_argument(
        "--list-stacks",
        action="store_true",
        help="Print supported primary stacks and exit.",
    )
    parser.add_argument(
        "--list-manifests",
        action="store_true",
        help="Print available manifests and exit.",
    )
    return parser


def slugify(value: str) -> str:
    """Return a deterministic repo slug."""

    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "generated-repo"


def python_package_name(slug: str) -> str:
    """Return a safe python package name."""

    return slug.replace("-", "_")


def phoenix_app_name(slug: str) -> str:
    """Return a safe phoenix app name."""

    return slug.replace("-", "_")


def phoenix_module_name(slug: str) -> str:
    """Return a CamelCase phoenix module prefix."""

    return "".join(part.capitalize() for part in slug.split("-"))


def repo_seed(slug: str) -> int:
    """Return a deterministic integer for port assignment."""

    return sum((index + 1) * ord(char) for index, char in enumerate(slug))


def parse_port_band(raw: str) -> tuple[int, int]:
    """Parse a manifest port band like 14000-14099."""

    start_raw, end_raw = raw.split("-", 1)
    return int(start_raw), int(end_raw)


def pick_port(band: str, slug: str, offset: int = 0) -> int:
    """Pick a deterministic port inside a band."""

    start, end = parse_port_band(band)
    width = end - start + 1
    return start + ((repo_seed(slug) + offset) % width)


def repo_root() -> Path:
    """Return the repository root."""

    return Path(__file__).resolve().parents[1]


def load_available_manifests() -> dict[str, dict[str, object]]:
    """Load all manifest files in the base repo."""

    manifest_dir = repo_root() / "manifests"
    manifests: dict[str, dict[str, object]] = {}
    for path in sorted(manifest_dir.glob("*.yaml")):
        manifests[path.stem] = parse_manifest(path)
    return manifests


def print_catalog(title: str, entries: dict[str, str]) -> int:
    """Print one catalog and exit."""

    print(title)
    for key, description in sorted(entries.items()):
        print(f"- {key}: {description}")
    return 0


def default_manifests_for(archetype: str, primary_stack: str, dokku: bool) -> list[str]:
    """Return the default manifest bundle for the requested repo shape."""

    selected = list(DEFAULT_MANIFESTS.get((archetype, primary_stack), []))
    if dokku and primary_stack in DOKKU_MANIFESTS and DOKKU_MANIFESTS[primary_stack] not in selected:
        selected.append(DOKKU_MANIFESTS[primary_stack])
    return selected


def infer_support_services(archetype: str, primary_stack: str, selected_manifests: list[str]) -> list[str]:
    """Infer which backing services belong in the generated compose files."""

    if "multi-storage-zoo" in selected_manifests or archetype == "multi-storage-experiment":
        return ["redis", "mongo", "meilisearch", "timescaledb", "elasticsearch", "qdrant"]
    if "local-rag-base" in selected_manifests or archetype == "local-rag-system":
        return ["qdrant"]
    if primary_stack == "python-fastapi-uv-ruff-orjson-polars":
        return ["postgres", "redis"]
    if primary_stack in {"typescript-hono-bun", "rust-axum-modern", "go-echo", "elixir-phoenix"}:
        return ["postgres"]
    if primary_stack == "duckdb-trino-polars":
        return ["trino"]
    return []


def render_template(path: Path, values: dict[str, str]) -> str:
    """Render a template by replacing {{key}} placeholders."""

    rendered = path.read_text(encoding="utf-8")
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def ensure_target(target_dir: Path, force: bool, dry_run: bool) -> None:
    """Validate that the target directory is writable."""

    if target_dir.exists():
        if any(target_dir.iterdir()) and not force:
            raise ValueError(
                f"Target directory '{target_dir}' already exists and is not empty. Use --force to continue."
            )
        return
    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)


def format_bullets(items: list[str]) -> str:
    """Format a list as markdown bullets."""

    return "\n".join(f"- {item}" for item in items)


def format_yaml_list(items: list[str], indent: int = 2) -> str:
    """Format a list as yaml lines."""

    prefix = " " * indent
    return "\n".join(f"{prefix}- {item}" for item in items) if items else f"{prefix}- none"


def format_yaml_mapping(items: dict[str, str], indent: int = 2) -> str:
    """Format a string mapping as yaml lines."""

    prefix = " " * indent
    return "\n".join(f"{prefix}{key}: {value}" for key, value in items.items())


def build_support_service_blocks(
    services: list[str],
    slug: str,
    dev_or_test: str,
    data_port_band: str,
) -> tuple[str, str, dict[str, int]]:
    """Return compose service blocks, depends_on block, and assigned ports."""

    if not services:
        return "", "", {}

    compose_services: list[str] = []
    ports: dict[str, int] = {}
    for offset, service_name in enumerate(services, start=1):
        preset = SERVICE_PRESETS[service_name]
        assigned_port = pick_port(data_port_band, slug, offset * 7)
        ports[service_name] = assigned_port
        env_lines = list(preset["env"])
        env_block = ""
        if env_lines:
            env_block = "\n    environment:\n" + "\n".join(f"      - {line}" for line in env_lines)
        volume_root = f"./docker/volumes/{dev_or_test}/{service_name}"
        block = (
            f"  {service_name}:\n"
            f"    image: {preset['image']}\n"
            f"{env_block}\n"
            f"    ports:\n"
            f"      - \"{assigned_port}:{preset['container_port']}\"\n"
            f"    volumes:\n"
            f"      - {volume_root}:{preset['volume_path']}\n"
        )
        compose_services.append(block.rstrip())

    depends_on = "    depends_on:\n" + "\n".join(f"      - {service}" for service in services)
    return depends_on, "\n".join(compose_services), ports


def build_env_files(services: list[str], slug: str, ports: dict[str, int], test_ports: dict[str, int]) -> dict[str, str]:
    """Build .env and .env.test content."""

    lines = [f"APP_ENV=dev", f"APP_NAME={slug}"]
    test_lines = [f"APP_ENV=test", f"APP_NAME={slug}-test"]

    if "postgres" in services or "timescaledb" in services:
        sql_service = "timescaledb" if "timescaledb" in services else "postgres"
        lines.append(f"DATABASE_URL=postgresql://app:app@127.0.0.1:{ports[sql_service]}/app")
        test_lines.append(
            f"TEST_DATABASE_URL=postgresql://app:app@127.0.0.1:{test_ports[sql_service]}/app"
        )
    if "redis" in services:
        lines.append(f"REDIS_URL=redis://127.0.0.1:{ports['redis']}/0")
        test_lines.append(f"TEST_REDIS_URL=redis://127.0.0.1:{test_ports['redis']}/0")
    if "mongo" in services:
        lines.append(f"MONGO_URL=mongodb://127.0.0.1:{ports['mongo']}")
        test_lines.append(f"TEST_MONGO_URL=mongodb://127.0.0.1:{test_ports['mongo']}")
    if "meilisearch" in services:
        lines.append(f"MEILI_URL=http://127.0.0.1:{ports['meilisearch']}")
        test_lines.append(f"TEST_MEILI_URL=http://127.0.0.1:{test_ports['meilisearch']}")
    if "elasticsearch" in services:
        lines.append(f"ELASTICSEARCH_URL=http://127.0.0.1:{ports['elasticsearch']}")
        test_lines.append(f"TEST_ELASTICSEARCH_URL=http://127.0.0.1:{test_ports['elasticsearch']}")
    if "qdrant" in services:
        lines.append(f"QDRANT_URL=http://127.0.0.1:{ports['qdrant']}")
        test_lines.append(f"TEST_QDRANT_URL=http://127.0.0.1:{test_ports['qdrant']}")
    if "trino" in services:
        lines.append(f"TRINO_URL=http://127.0.0.1:{ports['trino']}")
        test_lines.append(f"TEST_TRINO_URL=http://127.0.0.1:{test_ports['trino']}")

    return {
        ".env": "\n".join(lines) + "\n",
        ".env.test": "\n".join(test_lines) + "\n",
        ".env.example": "\n".join(lines) + "\n",
        ".env.test.example": "\n".join(test_lines) + "\n",
    }


def build_docs(repo_name: str, description: str, archetype: str, profile: StackProfile, manifests: list[str]) -> dict[str, str]:
    """Return repo-purpose and repo-layout docs."""

    repo_purpose = f"""# Repo Purpose

`{repo_name}` is a {ARCHETYPES[archetype].lower()}

Primary stack:

- {profile.display_name}

Selected manifest hints:

{format_bullets(manifests)}
"""

    repo_layout = f"""# Repo Layout

- `README.md`: repo entrypoint
- `AGENT.md` and `CLAUDE.md`: assistant routing entrypoints
- `docs/`: repo-level purpose, layout, and deployment notes
- `manifests/project-profile.yaml`: generated project profile
- `{profile.route_path}`: primary route or entrypoint surface
- `tests/smoke/`: smallest happy-path checks
- `tests/integration/`: real boundary checks when needed
- `docker-compose.yml` and `docker-compose.test.yml`: isolated primary and test stacks
"""
    return {
        "docs/repo-purpose.md": repo_purpose,
        "docs/repo-layout.md": repo_layout,
    }


def render_readme(
    repo_name: str,
    description: str,
    archetype: str,
    profile: StackProfile,
    manifests: list[str],
    dokku: bool,
    prompt_first: bool,
    docker_enabled: bool,
    app_port: int,
    compose_project_name_dev: str,
    compose_project_name_test: str,
    support_ports: dict[str, int],
    test_support_ports: dict[str, int],
) -> str:
    """Render the top-level README from template."""

    template_path = repo_root() / "templates/readme/README.template.md"
    compose_section = ""
    if docker_enabled:
        lines = [
            "## Local Infra",
            "",
            f"- app: `http://127.0.0.1:{app_port}`",
            f"- Compose dev name: `{compose_project_name_dev}`",
            f"- Compose test name: `{compose_project_name_test}`",
        ]
        for service, port in support_ports.items():
            lines.append(f"- {service} dev port: `{port}`")
        for service, port in test_support_ports.items():
            lines.append(f"- {service} test port: `{port}`")
        compose_section = "\n".join(lines)

    dokku_section = ""
    if dokku:
        dokku_section = "\n".join(
            [
                "## Dokku",
                "",
                "- `Procfile` and `app.json` are included as starters.",
                "- `scripts/smoke/deploy_smoke.sh` should stay small and explicit.",
            ]
        )

    values = {
        "repo_name": repo_name,
        "description": description,
        "archetype": archetype,
        "primary_stack_display": profile.display_name,
        "selected_manifests": ", ".join(manifests),
        "dokku_status": "enabled" if dokku else "not-enabled",
        "prompt_first_status": "enabled" if prompt_first else "not-enabled",
        "workflow_bullets": format_bullets(
            [
                "start from the generated project profile before expanding context",
                "add one smoke test for each new happy path",
                "add a real integration test when a feature crosses a storage or service boundary",
            ]
        ),
        "compose_section": compose_section,
        "dokku_section": dokku_section,
    }
    return render_template(template_path, values)


def render_agent_and_claude(archetype: str, primary_stack: str, manifests: list[str]) -> dict[str, str]:
    """Render AGENT.md and CLAUDE.md."""

    values = {
        "archetype": archetype,
        "primary_stack": primary_stack,
        "selected_manifests": ", ".join(manifests),
    }
    return {
        "AGENT.md": render_template(repo_root() / "templates/agent-md/AGENT.template.md", values),
        "CLAUDE.md": render_template(repo_root() / "templates/claude-md/CLAUDE.template.md", values),
    }


def render_gitignore(profile: StackProfile) -> str:
    """Render the .gitignore template."""

    stack_gitignore = "\n".join(profile.stack_gitignore)
    return render_template(
        repo_root() / "templates/gitignore/.gitignore.template",
        {"stack_gitignore": stack_gitignore},
    )


def render_profile_summary(
    repo_name: str,
    slug: str,
    description: str,
    archetype: str,
    primary_stack: str,
    manifests: list[str],
    docker_enabled: bool,
    dokku: bool,
    prompt_first: bool,
    smoke_tests: bool,
    integration_tests: bool,
    seed_data: bool,
    compose_project_name_dev: str,
    compose_project_name_test: str,
    compose_files: list[str],
    port_map: dict[str, int],
    starter_paths: dict[str, str],
    validation_commands: list[str],
) -> str:
    """Render the generated profile summary."""

    values = {
        "repo_name": repo_name,
        "repo_slug": slug,
        "description": description,
        "archetype": archetype,
        "primary_stack": primary_stack,
        "selected_manifest_lines": format_yaml_list(manifests),
        "dokku_enabled": str(dokku).lower(),
        "prompt_first_enabled": str(prompt_first).lower(),
        "smoke_tests_enabled": str(smoke_tests).lower(),
        "integration_tests_enabled": str(integration_tests).lower(),
        "seed_data_enabled": str(seed_data).lower(),
        "compose_file_lines": format_yaml_list(compose_files if docker_enabled else ["none"]),
        "compose_project_name_dev": compose_project_name_dev,
        "compose_project_name_test": compose_project_name_test,
        "port_lines": format_yaml_mapping({key: str(value) for key, value in port_map.items()}),
        "starter_path_lines": format_yaml_mapping(starter_paths),
        "context_entrypoint_lines": format_yaml_list(
            ["README.md", "AGENT.md", "CLAUDE.md", "manifests/project-profile.yaml"]
        ),
        "validation_command_lines": format_yaml_list(validation_commands),
        "compose_invariant_lines": format_yaml_list(
            [
                "docker-compose.yml and docker-compose.test.yml both declare a top-level name",
                "dev and test Compose names differ",
                "test Compose name ends with -test",
                "dev and test host ports do not overlap",
                "dev data stays under docker/volumes/dev",
                "test data stays under docker/volumes/test",
            ]
        ),
    }
    return render_template(
        repo_root() / "templates/manifest/profile-summary.template.yaml",
        values,
    )


def render_dokku_files(slug: str, app_port: int) -> dict[str, str]:
    """Render Dokku starter files."""

    deployment_notes = render_template(
        repo_root() / "templates/dokku/Dokku.template.md",
        {
            "repo_slug": slug,
            "app_port": str(app_port),
            "release_command": "replace-with-your-migration-command",
        },
    )
    app_json = {
        "name": slug,
        "description": f"{slug} starter service",
        "scripts": {"dokku:postdeploy": "./scripts/smoke/deploy_smoke.sh"},
        "env": {
            "APP_ENV": {
                "description": "Runtime environment name.",
                "value": "production",
            }
        },
    }
    return {
        "docs/deployment.md": deployment_notes,
        "Procfile": "web: replace-with-your-runtime-command\nrelease: replace-with-your-release-command\n",
        "app.json": json.dumps(app_json, indent=2) + "\n",
        "scripts/smoke/deploy_smoke.sh": "#!/usr/bin/env bash\nset -euo pipefail\ncurl -fsS \"${APP_BASE_URL}/healthz\"\n",
    }


def render_prompt_files(repo_name: str, profile: StackProfile) -> dict[str, str]:
    """Render prompt-first starter files."""

    values = {
        "repo_name": repo_name,
        "starter_route_path": profile.route_path,
        "starter_test_path": profile.smoke_path,
        "starter_integration_test_path": profile.integration_path,
        "starter_seed_path": profile.seed_path,
    }
    return {
        "PROMPTS.md": render_template(repo_root() / "templates/prompt-first/PROMPTS.md.template", values),
        ".prompts/001-bootstrap-repo.txt": render_template(
            repo_root() / "templates/prompt-first/001-bootstrap.template.txt",
            values,
        ),
        ".prompts/002-refine-test-surface.txt": render_template(
            repo_root() / "templates/prompt-first/002-refine.template.txt",
            values,
        ),
    }


def render_python_starters(package_name: str, profile: StackProfile) -> dict[str, str]:
    """Render Python starter app and tests."""

    route_content = ""
    app_content = ""
    if profile.route_path == "app/api/reports.py":
        route_content = """from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary")
def list_summaries() -> list[dict[str, str]]:
    return [{"report_id": "daily-signups", "status": "ready"}]
"""
        app_content = """from fastapi import FastAPI

from app.api.reports import router as reports_router


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(reports_router)
    return app


app = create_app()
"""
    elif profile.route_path == "app/index_documents.py":
        route_content = """from pathlib import Path


def main() -> None:
    corpus = Path("data/corpus")
    print(f"Index documents from {corpus}")


if __name__ == "__main__":
    main()
"""
        app_content = ""
    else:
        route_content = """def main() -> None:
    print("Replace this starter with the first real implementation.")


if __name__ == "__main__":
    main()
"""

    smoke_test = render_template(
        repo_root() / "templates/smoke-tests/smoke_test.template.py",
        {
            "import_block": "from fastapi.testclient import TestClient\n\nfrom app.main import create_app",
            "app_factory": "create_app",
            "client_factory": "TestClient",
            "health_path": "/healthz",
        },
    )
    if profile.route_path != "app/api/reports.py":
        smoke_test = """def test_smoke_placeholder() -> None:\n    assert True\n"""

    integration_test = render_template(
        repo_root() / "templates/integration-tests/integration_test.template.py",
        {},
    )
    seed_data = render_template(
        repo_root() / "templates/seed-data/seed_data.template.py",
        {"seed_filename": "seed-data.txt"},
    )

    files = {}
    if app_content:
        files["app/main.py"] = app_content
    files[profile.route_path] = route_content
    files[profile.smoke_path] = smoke_test
    files[profile.integration_path] = integration_test
    files[profile.seed_path] = seed_data
    files["app/__init__.py"] = ""
    if profile.route_path.startswith("app/api/"):
        files["app/api/__init__.py"] = ""
    return files


def render_prompt_meta_starters() -> dict[str, str]:
    """Render prompt-first validation helper files."""

    return {
        "scripts/check_repo.py": """#!/usr/bin/env python3\n\"\"\"Check the minimal prompt-first repo surface exists.\"\"\"\n\nfrom pathlib import Path\n\n\ndef main() -> None:\n    required = [Path(\"README.md\"), Path(\"AGENT.md\"), Path(\"CLAUDE.md\")]\n    missing = [path.as_posix() for path in required if not path.exists()]\n    if missing:\n        raise SystemExit(f\"Missing required files: {missing}\")\n    print(\"repo surface looks present\")\n\n\nif __name__ == \"__main__\":\n    main()\n""",
        "scripts/check_generated_profile.py": """#!/usr/bin/env python3\n\"\"\"Check the generated profile file exists.\"\"\"\n\nfrom pathlib import Path\n\n\ndef main() -> None:\n    profile = Path(\".generated-profile.yaml\")\n    if not profile.exists():\n        raise SystemExit(\".generated-profile.yaml is missing\")\n    print(\"generated profile exists\")\n\n\nif __name__ == \"__main__\":\n    main()\n""",
        "scripts/validate_repo.py": """#!/usr/bin/env python3\n\"\"\"Validate the prompt-first starter repo surface.\"\"\"\n\nfrom pathlib import Path\n\n\ndef main() -> None:\n    required = [\n        Path(\"README.md\"),\n        Path(\"AGENT.md\"),\n        Path(\"CLAUDE.md\"),\n        Path(\"manifests/project-profile.yaml\"),\n    ]\n    missing = [path.as_posix() for path in required if not path.exists()]\n    if missing:\n        raise SystemExit(f\"Missing required files: {missing}\")\n\n    prompt_dir = Path(\".prompts\")\n    prompt_files = sorted(path.name for path in prompt_dir.glob(\"*.txt\"))\n    expected = [f\"{index:03d}-{name.split('-', 1)[1]}\" for index, name in enumerate(prompt_files, start=1)]\n    if prompt_files and prompt_files != expected:\n        raise SystemExit(f\"Prompt files must stay monotonic: {prompt_files}\")\n\n    print(\"repo validation passed\")\n\n\nif __name__ == \"__main__\":\n    main()\n""",
        "scripts/seed_data.py": """#!/usr/bin/env python3\n\"\"\"Write deterministic prompt-first starter notes.\"\"\"\n\nfrom pathlib import Path\n\n\ndef main() -> None:\n    target = Path(\"docs/generated-notes.txt\")\n    target.parent.mkdir(parents=True, exist_ok=True)\n    target.write_text(\"replace with deterministic repo notes\\n\", encoding=\"utf-8\")\n    print(f\"Wrote {target}\")\n\n\nif __name__ == \"__main__\":\n    main()\n""",
    }


def render_typescript_starters() -> dict[str, str]:
    """Render TypeScript starter app and tests."""

    return {
        "src/index.ts": """import { Hono } from "hono";\nimport { reportsRouter } from "./routes/reports";\n\nconst app = new Hono();\n\napp.get("/healthz", (context) => context.json({ status: "ok" }));\napp.route("/", reportsRouter);\n\nexport default app;\n""",
        "src/routes/reports.tsx": """import { Hono } from "hono";\n\nexport const reportsRouter = new Hono();\n\nreportsRouter.get("/reports/summary", (context) => {\n  return context.html(<div>replace with a real report summary route</div>);\n});\n""",
        "tests/smoke/health.smoke.ts": """import { describe, expect, test } from "bun:test";\nimport app from "../../src/index";\n\ndescribe("health smoke", () => {\n  test("GET /healthz", async () => {\n    const response = await app.request("/healthz");\n    expect(response.status).toBe(200);\n  });\n});\n""",
        "tests/integration/report-runs.int.ts": """import { afterAll, beforeAll, describe, expect, test } from "bun:test";\n\nbeforeAll(() => {\n  // Replace this with docker compose up -d against docker-compose.test.yml.\n});\n\nafterAll(() => {\n  // Replace this with docker compose down -v against docker-compose.test.yml.\n});\n\ndescribe("report runs integration", () => {\n  test("replace with one real DB round trip", async () => {\n    expect(true).toBe(true);\n  });\n});\n""",
        "scripts/seed-data.ts": """import { mkdirSync, writeFileSync } from "node:fs";\n\nmkdirSync("docker/volumes/dev", { recursive: true });\nwriteFileSync(\n  "docker/volumes/dev/seed-data.json",\n  JSON.stringify([{ reportId: "daily-signups", status: "ready" }], null, 2),\n);\n""",
    }


def render_rust_starters() -> dict[str, str]:
    """Render Rust starter app and tests."""

    return {
        "src/main.rs": """use axum::{routing::get, Json, Router};\n\n#[tokio::main]\nasync fn main() {\n    let app = Router::new()\n        .route(\"/healthz\", get(|| async { Json(serde_json::json!({\"status\": \"ok\"})) }));\n\n    let listener = tokio::net::TcpListener::bind(\"0.0.0.0:3000\").await.unwrap();\n    axum::serve(listener, app).await.unwrap();\n}\n""",
        "tests/smoke_health.rs": """#[test]\nfn health_smoke_placeholder() {\n    assert!(true);\n}\n""",
        "tests/report_runs_integration.rs": """#[test]\nfn report_runs_integration_placeholder() {\n    // Replace with docker-compose.test.yml boot plus one real round-trip assertion.\n    assert!(true);\n}\n""",
        "scripts/seed_data.sql": "insert into report_runs (tenant_id, report_id, total_events) values ('acme', 'daily-signups', 42);\n",
    }


def render_go_starters() -> dict[str, str]:
    """Render Go starter app and tests."""

    return {
        "cmd/server/main.go": """package main\n\nimport (\n\t\"net/http\"\n\n\t\"github.com/labstack/echo/v4\"\n)\n\nfunc main() {\n\te := echo.New()\n\te.GET(\"/healthz\", func(c echo.Context) error {\n\t\treturn c.JSON(http.StatusOK, map[string]string{\"status\": \"ok\"})\n\t})\n\te.Logger.Fatal(e.Start(\":8080\"))\n}\n""",
        "tests/smoke/health_test.go": """package smoke\n\nimport \"testing\"\n\nfunc TestHealthSmoke(t *testing.T) {\n\t// Replace with a real boot or handler smoke check.\n}\n""",
        "tests/integration/report_runs_test.go": """package integration\n\nimport \"testing\"\n\nfunc TestReportRunsIntegration(t *testing.T) {\n\t// Replace with docker-compose.test.yml boot plus one real boundary assertion.\n}\n""",
        "scripts/seed_data.sql": "insert into report_runs (tenant_id, report_id, total_events) values ('acme', 'daily-signups', 42);\n",
    }


def render_phoenix_starters(slug: str) -> dict[str, str]:
    """Render Phoenix starter app and tests."""

    app_name = phoenix_app_name(slug)
    module_name = phoenix_module_name(slug)
    return {
        f"lib/{app_name}_web/router.ex": f"""defmodule {module_name}Web.Router do\n  use {module_name}Web, :router\n\n  scope \"/\", {module_name}Web do\n    pipe_through :browser\n\n    get \"/healthz\", HealthController, :show\n  end\nend\n""",
        f"lib/{app_name}_web/controllers/health_controller.ex": f"""defmodule {module_name}Web.HealthController do\n  use {module_name}Web, :controller\n\n  def show(conn, _params) do\n    json(conn, %{{status: \"ok\"}})\n  end\nend\n""",
        f"test/{app_name}_web/controllers/health_controller_test.exs": """defmodule HealthControllerTest do\n  use ExUnit.Case, async: true\n\n  test \"placeholder\" do\n    assert true\n  end\nend\n""",
        f"test/{app_name}/reporting_test.exs": """defmodule ReportingTest do\n  use ExUnit.Case, async: false\n\n  test \"replace with real DB round trip\" do\n    assert true\n  end\nend\n""",
        "priv/repo/seeds.exs": "IO.puts(\"replace with deterministic seed data\")\n",
    }


def starter_files_for_stack(primary_stack: str, slug: str) -> dict[str, str]:
    """Return the starter files for the selected primary stack."""

    if primary_stack == "prompt-first-repo":
        return render_prompt_meta_starters()
    if primary_stack in {"python-fastapi-uv-ruff-orjson-polars", "qdrant", "duckdb-trino-polars", "redis-keydb-mongo"}:
        return render_python_starters(python_package_name(slug), STACKS[primary_stack])
    if primary_stack == "typescript-hono-bun":
        return render_typescript_starters()
    if primary_stack == "rust-axum-modern":
        return render_rust_starters()
    if primary_stack == "go-echo":
        return render_go_starters()
    if primary_stack == "elixir-phoenix":
        return render_phoenix_starters(slug)
    raise ValueError(f"Unsupported primary stack: {primary_stack}")


def write_files(target_dir: Path, files: dict[str, str], dry_run: bool) -> None:
    """Write generated files to disk."""

    for relative_path, content in sorted(files.items()):
        destination = target_dir / relative_path
        if dry_run:
            print(destination.relative_to(target_dir).as_posix())
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")


def resolved_starter_paths(primary_stack: str, slug: str) -> dict[str, str]:
    """Return the starter file paths visible in the generated profile."""

    profile = STACKS[primary_stack]
    if primary_stack == "elixir-phoenix":
        app_name = phoenix_app_name(slug)
        return {
            "route": f"lib/{app_name}_web/router.ex",
            "smoke": f"test/{app_name}_web/controllers/health_controller_test.exs",
            "integration": f"test/{app_name}/reporting_test.exs",
            "seed": "priv/repo/seeds.exs",
        }
    if primary_stack == "prompt-first-repo":
        return {
            "route": "README.md",
            "smoke": "scripts/check_repo.py",
            "integration": "scripts/validate_repo.py",
            "seed": "scripts/seed_data.py",
        }
    return {
        "route": profile.route_path,
        "smoke": profile.smoke_path,
        "integration": profile.integration_path,
        "seed": profile.seed_path,
    }


def validate_bootstrap_plan(
    *,
    compose_project_name_dev: str,
    compose_project_name_test: str,
    app_port: int,
    test_app_port: int,
    dev_support_ports: dict[str, int],
    test_support_ports: dict[str, int],
) -> None:
    """Validate the generated Compose naming and port plan before writing files."""

    if not compose_project_name_dev.strip():
        raise ValueError("compose_project_name_dev must be non-empty")
    if not compose_project_name_test.strip():
        raise ValueError("compose_project_name_test must be non-empty")
    if compose_project_name_dev == compose_project_name_test:
        raise ValueError("Compose dev and test project names must differ")
    if not compose_project_name_test.endswith("-test"):
        raise ValueError("Compose test project name must end with '-test'")

    used_ports = {"app_dev": app_port, "app_test": test_app_port, **dev_support_ports, **test_support_ports}
    seen: dict[int, str] = {}
    for label, port in used_ports.items():
        if port in seen:
            raise ValueError(f"Port collision between {seen[port]} and {label}: {port}")
        seen[port] = label


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv[1:])

    manifests = load_available_manifests()

    if args.list_archetypes:
        return print_catalog("Archetypes", ARCHETYPES)
    if args.list_stacks:
        return print_catalog("Primary stacks", {key: value.description for key, value in STACKS.items()})
    if args.list_manifests:
        return print_catalog(
            "Manifests",
            {name: str(data.get("description", "")) for name, data in manifests.items()},
        )

    if not args.repo_name:
        parser.error("repo_name is required unless a --list-* flag is used")
    if not args.archetype:
        parser.error("--archetype is required")
    if not args.primary_stack:
        parser.error("--primary-stack is required")

    repo_name = args.repo_name
    slug = slugify(repo_name)
    target_dir = Path(args.target_dir or slug).expanduser().resolve()
    ensure_target(target_dir, force=args.force, dry_run=args.dry_run)

    if args.primary_stack not in STACKS:
        raise ValueError(f"Unsupported stack: {args.primary_stack}")
    if args.archetype not in ARCHETYPES:
        raise ValueError(f"Unsupported archetype: {args.archetype}")

    selected_manifests = sorted(
        set(
            args.manifest
            or default_manifests_for(args.archetype, args.primary_stack, args.dokku)
        )
    )
    for manifest_name in selected_manifests:
        if manifest_name not in manifests:
            raise ValueError(f"Unknown manifest: {manifest_name}")

    docker_enabled = args.docker_layout or bool(
        infer_support_services(args.archetype, args.primary_stack, selected_manifests)
    )
    prompt_first = args.prompt_first or args.archetype == "prompt-first-repo"
    profile = STACKS[args.primary_stack]
    description = f"Starter repo for {repo_name} using {profile.display_name}."

    selected_manifest_data = [manifests[name] for name in selected_manifests]
    if selected_manifest_data:
        primary_manifest = selected_manifest_data[0]
    else:
        primary_manifest = {
            "compose_project_name_dev": "{repo_slug}",
            "compose_project_name_test": "{repo_slug}-test",
            "port_band_app_dev": "14000-14099",
            "port_band_app_test": "15000-15099",
            "port_band_data_dev": "24000-24099",
            "port_band_data_test": "25000-25099",
        }

    compose_project_name_dev = str(primary_manifest["compose_project_name_dev"]).replace(
        "{repo_slug}", slug
    )
    compose_project_name_test = str(primary_manifest["compose_project_name_test"]).replace(
        "{repo_slug}", slug
    )
    app_port = pick_port(str(primary_manifest["port_band_app_dev"]), slug)
    test_app_port = pick_port(str(primary_manifest["port_band_app_test"]), slug)

    support_services = infer_support_services(args.archetype, args.primary_stack, selected_manifests)
    dev_depends_on, dev_support_block, dev_support_ports = build_support_service_blocks(
        support_services,
        slug,
        "dev",
        str(primary_manifest["port_band_data_dev"]),
    )
    test_depends_on, test_support_block, test_support_ports = build_support_service_blocks(
        support_services,
        slug,
        "test",
        str(primary_manifest["port_band_data_test"]),
    )

    generated_files: dict[str, str] = {}
    generated_files.update(
        render_agent_and_claude(args.archetype, args.primary_stack, selected_manifests)
    )
    generated_files["README.md"] = render_readme(
        repo_name,
        description,
        args.archetype,
        profile,
        selected_manifests,
        args.dokku,
        prompt_first,
        docker_enabled,
        app_port,
        compose_project_name_dev,
        compose_project_name_test,
        dev_support_ports,
        test_support_ports,
    )
    generated_files[".gitignore"] = render_gitignore(profile)
    generated_files.update(build_docs(repo_name, description, args.archetype, profile, selected_manifests))

    starter_paths = resolved_starter_paths(args.primary_stack, slug)
    port_map = {"app_dev": app_port, "app_test": test_app_port}
    port_map.update({f"{name}_dev": port for name, port in dev_support_ports.items()})
    port_map.update({f"{name}_test": port for name, port in test_support_ports.items()})
    validation_commands = ["python scripts/validate_repo.py"] if args.primary_stack == "prompt-first-repo" else []
    if docker_enabled:
        validation_commands.append("docker compose -f docker-compose.test.yml config")
    validate_bootstrap_plan(
        compose_project_name_dev=compose_project_name_dev,
        compose_project_name_test=compose_project_name_test,
        app_port=app_port,
        test_app_port=test_app_port,
        dev_support_ports={f"{name}_dev": port for name, port in dev_support_ports.items()},
        test_support_ports={f"{name}_test": port for name, port in test_support_ports.items()},
    )
    profile_summary = render_profile_summary(
        repo_name=repo_name,
        slug=slug,
        description=description,
        archetype=args.archetype,
        primary_stack=args.primary_stack,
        manifests=selected_manifests,
        docker_enabled=docker_enabled,
        dokku=args.dokku,
        prompt_first=prompt_first,
        smoke_tests=args.smoke_tests,
        integration_tests=args.integration_tests,
        seed_data=args.seed_data,
        compose_project_name_dev=compose_project_name_dev,
        compose_project_name_test=compose_project_name_test,
        compose_files=["docker-compose.yml", "docker-compose.test.yml"],
        port_map=port_map,
        starter_paths=starter_paths,
        validation_commands=validation_commands or ["echo no extra validation commands configured"],
    )
    generated_files["manifests/project-profile.yaml"] = profile_summary
    if not args.no_profile:
        generated_files[".generated-profile.yaml"] = profile_summary

    starter_files = starter_files_for_stack(args.primary_stack, slug)
    route_only_keys = set()
    if args.primary_stack == "python-fastapi-uv-ruff-orjson-polars":
        route_only_keys.update({"app/main.py", profile.route_path, "app/__init__.py", "app/api/__init__.py"})
    elif args.primary_stack == "typescript-hono-bun":
        route_only_keys.update({"src/index.ts", profile.route_path})
    elif args.primary_stack == "rust-axum-modern":
        route_only_keys.update({"src/main.rs"})
    elif args.primary_stack == "go-echo":
        route_only_keys.update({"cmd/server/main.go"})
    elif args.primary_stack == "elixir-phoenix":
        route_only_keys.update({starter_paths["route"], f"lib/{phoenix_app_name(slug)}_web/controllers/health_controller.ex"})
    elif args.primary_stack == "prompt-first-repo":
        route_only_keys.update({"scripts/validate_repo.py"})
    else:
        route_only_keys.update({starter_paths["route"], "app/__init__.py"})
    for relative_path, content in starter_files.items():
        should_write = relative_path in route_only_keys
        if args.smoke_tests and relative_path == starter_paths["smoke"]:
            should_write = True
        if args.integration_tests and relative_path == starter_paths["integration"]:
            should_write = True
        if args.seed_data and relative_path == starter_paths["seed"]:
            should_write = True
        if should_write:
            generated_files[relative_path] = content

    if docker_enabled:
        compose_values = {
            "compose_project_name": compose_project_name_dev,
            "app_image": profile.app_image,
            "app_command": profile.app_command,
            "app_port": str(app_port),
            "app_container_port": str(profile.app_container_port),
            "app_depends_on_block": dev_depends_on,
            "support_services_block": dev_support_block,
        }
        test_compose_values = {
            "compose_project_name": compose_project_name_test,
            "app_image": profile.app_image,
            "test_command": profile.test_command,
            "app_port": str(test_app_port),
            "app_container_port": str(profile.app_container_port),
            "app_depends_on_block": test_depends_on,
            "support_services_block": test_support_block,
        }
        generated_files["docker-compose.yml"] = render_template(
            repo_root() / "templates/compose/docker-compose.template.yaml",
            compose_values,
        )
        generated_files["docker-compose.test.yml"] = render_template(
            repo_root() / "templates/compose/docker-compose-test.template.yaml",
            test_compose_values,
        )
        generated_files.update(build_env_files(support_services, slug, dev_support_ports, test_support_ports))

    if profile.extra_template:
        generated_files["docs/stack-notes.md"] = render_template(
            repo_root() / profile.extra_template,
            {},
        )

    if prompt_first:
        generated_files.update(render_prompt_files(repo_name, profile))

    if args.dokku:
        generated_files.update(render_dokku_files(slug, profile.app_container_port))

    if args.dry_run:
        print(f"Target: {target_dir}")
        print("Planned files:")
    else:
        for directory in profile.directories:
            (target_dir / directory).mkdir(parents=True, exist_ok=True)
        if args.dokku:
            (target_dir / "scripts/smoke").mkdir(parents=True, exist_ok=True)
    write_files(target_dir, generated_files, args.dry_run)

    if args.dry_run:
        return 0

    print(f"Generated starter repo at {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
