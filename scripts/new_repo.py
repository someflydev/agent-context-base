#!/usr/bin/env python3
"""Bootstrap a new repo from the agent-context-base conventions.

Examples:
    python scripts/new_repo.py analytics-api \
        --archetype backend-api-service \
        --primary-stack python-fastapi-uv-ruff-orjson-polars \
        --smoke-tests \
        --integration-tests \
        --seed-data \
        --include-root-readme \
        --include-docs-dir \
        --dokku

    python scripts/new_repo.py prompt-kit \
        --archetype prompt-first-repo \
        --primary-stack prompt-first-repo \
        --prompt-first \
        --target-dir /tmp/prompt-kit
"""

from __future__ import annotations

import argparse
import ast
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
    "polyglot-lab": "Multi-language exploratory repo with each surface clearly owned and no shared production seam.",
    "data-acquisition-service": "Service that acquires, archives, normalizes, and persists external data behind stable boundaries.",
    "multi-source-sync-platform": "Platform that coordinates recurring multi-source syncs with checkpoints and idempotent persistence.",
    "multi-backend-service": "Two or three backend services in different languages coordinating over an explicit designed seam.",
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
    "kotlin-http4k-exposed": StackProfile(
        description="Kotlin HTTP service using http4k and Exposed.",
        display_name="Kotlin + http4k + Exposed",
        app_image="gradle:8.10.2-jdk21",
        app_command='sh -lc "gradle run"',
        test_command='sh -lc "gradle test"',
        app_container_port=8080,
        route_path="src/main/kotlin/app/Main.kt",
        smoke_path="src/test/kotlin/app/HealthSmokeTest.kt",
        integration_path="src/test/kotlin/app/ReportRunsIntegrationTest.kt",
        seed_path="scripts/seed_data.sql",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "src/main/kotlin/app",
            "src/test/kotlin/app",
        ),
        stack_gitignore=(".gradle/", "build/"),
    ),
    "zig-zap-jetzig": StackProfile(
        description="Zig backend service using Zap and Jetzig-style view patterns.",
        display_name="Zig + Zap + Jetzig",
        app_image="ziglang/zig:0.15.1",
        app_command='sh -lc "mkdir -p zig-out/bin && zig build-exe src/main.zig -femit-bin=zig-out/bin/app && ./zig-out/bin/app"',
        test_command='sh -lc "zig test tests/smoke/health_test.zig"',
        app_container_port=3000,
        route_path="src/main.zig",
        smoke_path="tests/smoke/health_test.zig",
        integration_path="tests/integration/report_runs_test.zig",
        seed_path="scripts/seed_data.zig",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "src",
            "src/http",
            "src/views",
            "tests/smoke",
            "tests/integration",
        ),
        stack_gitignore=("zig-cache/", "zig-out/"),
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
        route_path=".prompts/001-bootstrap-repo.txt",
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
    "nim-jester-happyx": StackProfile(
        description="Nim backend service using Jester for routing and HappyX for HTML fragment surfaces.",
        display_name="Nim + Jester + HappyX",
        app_image="nimlang/nim:2.0.2",  # TODO: verify Nim Docker image tag
        app_command='sh -lc "nimble run"',  # TODO: verify nimble task name matches project
        test_command='sh -lc "nimble test"',
        app_container_port=5000,  # TODO: verify Jester port matches app configuration
        route_path="src/main.nim",
        smoke_path="tests/smoke/health_smoke.nim",
        integration_path="tests/integration/report_runs_integration.nim",
        seed_path="scripts/seed_data.nim",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "src/fragments",
            "src/http",
            "src/services",
            "tests/smoke",
            "tests/integration",
        ),
        stack_gitignore=("nimcache/", ".cache/"),
    ),
    "scala-tapir-http4s-zio": StackProfile(
        description="Scala backend service using Tapir, http4s, and ZIO for typed HTTP endpoints.",
        display_name="Scala + Tapir + http4s + ZIO",
        app_image="sbtscala/scala-sbt:eclipse-temurin-21_1.10.0_3.4.0",  # TODO: verify SBT image tag
        app_command='sh -lc "sbt run"',
        test_command='sh -lc "sbt test"',
        app_container_port=8080,
        route_path="src/main/scala/app/Main.scala",
        smoke_path="src/test/scala/app/HealthSmokeTest.scala",
        integration_path="src/test/scala/app/ReportRunsIntegrationTest.scala",
        seed_path="scripts/seed_data.sql",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "modules/domain",
            "modules/http",
            "modules/services",
            "project",
            "scripts",
            "src/main/scala/app",
            "src/test/scala/app",
        ),
        stack_gitignore=(".bsp/", "target/"),
    ),
    "clojure-kit-nextjdbc-hiccup": StackProfile(
        description="Clojure backend service using Kit-style wiring, next.jdbc, and Hiccup.",
        display_name="Clojure + Kit + next.jdbc + Hiccup",
        app_image="clojure:temurin-21-tools-deps",  # TODO: verify Clojure image tag
        app_command='sh -lc "clojure -M:run-dev"',  # TODO: verify :run-dev alias exists in deps.edn
        test_command='sh -lc "clojure -M:test"',
        app_container_port=3000,
        route_path="src/app/routes.clj",
        smoke_path="test/app/health_smoke_test.clj",
        integration_path="test/app/report_runs_integration_test.clj",
        seed_path="scripts/seed_data.sql",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "resources",
            "scripts",
            "src/app",
            "test/app",
        ),
        stack_gitignore=(".cpcache/", ".clj-kondo/"),
    ),
    "dart-dartfrog": StackProfile(
        description="Dart backend service using Dart Frog for JSON, fragment, and data endpoints.",
        display_name="Dart + Dart Frog",
        app_image="dart:3.3",  # TODO: verify Dart SDK image tag
        app_command='sh -lc "dart pub get && dart_frog serve"',  # TODO: verify serve command for Docker context
        test_command='sh -lc "dart test"',
        app_container_port=8080,
        route_path="routes/index.dart",
        smoke_path="test/health_smoke_test.dart",
        integration_path="test/report_runs_integration_test.dart",
        seed_path="scripts/seed_data.dart",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "lib",
            "manifests",
            "routes",
            "scripts",
            "test",
        ),
        stack_gitignore=(".dart_tool/", "build/"),
    ),
    "crystal-kemal-avram": StackProfile(
        description="Crystal HTTP service using Kemal for routing and Avram for PostgreSQL ORM.",
        display_name="Crystal + Kemal + Avram",
        app_image="84codes/crystal:latest-ubuntu-24.04",
        app_command='sh -lc "shards install && crystal run src/app.cr"',
        test_command='sh -lc "crystal spec"',
        app_container_port=3000,
        route_path="src/routes/reports.cr",
        smoke_path="spec/smoke/health_spec.cr",
        integration_path="spec/integration/report_runs_spec.cr",
        seed_path="scripts/seed_data.cr",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "src",
            "src/routes",
            "spec/smoke",
            "spec/integration",
        ),
        stack_gitignore=(".crystal", "bin/"),
    ),
    "ruby-hanami": StackProfile(
        description="Ruby HTTP service using Hanami for actions, views, and PostgreSQL persistence.",
        display_name="Ruby + Hanami",
        app_image="ruby:3.3-slim",
        app_command='sh -lc "bundle install && bundle exec hanami server --host 0.0.0.0 --port 2300"',
        test_command='sh -lc "bundle exec rspec"',
        app_container_port=2300,
        route_path="app/actions/reports/index.rb",
        smoke_path="spec/smoke/health_spec.rb",
        integration_path="spec/integration/report_runs_spec.rb",
        seed_path="scripts/seed_data.rb",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "app/actions/reports",
            "app/views/reports",
            "spec/smoke",
            "spec/integration",
        ),
        stack_gitignore=(".bundle",),
    ),
    "ocaml-dream-caqti-tyxml": StackProfile(
        description="OCaml HTTP service using Dream for routing, Caqti for PostgreSQL, and Tyxml for fragments.",
        display_name="OCaml + Dream + Caqti + Tyxml",
        app_image="ocaml/opam:ubuntu-24.04-ocaml-5.2",
        app_command='sh -lc "opam exec -- dune exec ./bin/main.exe"',
        test_command='sh -lc "opam exec -- dune runtest"',
        app_container_port=8080,
        route_path="bin/routes.ml",
        smoke_path="test/smoke/test_health.ml",
        integration_path="test/integration/test_report_runs.ml",
        seed_path="scripts/seed_data.ml",
        directories=(
            "docs",
            "docker/volumes/dev",
            "docker/volumes/test",
            "manifests",
            "scripts",
            "bin",
            "lib",
            "test/smoke",
            "test/integration",
        ),
        stack_gitignore=("_build",),
    ),
}


@dataclass(frozen=True)
class ExampleProject:
    codename: str
    title: str
    archetype: str
    primary_stack: str
    dokku: bool = False
    smoke_tests: bool = False
    integration_tests: bool = False
    seed_data: bool = False


@dataclass(frozen=True)
class RepoGenerationRequest:
    repo_name: str
    target_dir: Path
    archetype: str
    primary_stack: str
    manifests: list[str]
    dokku: bool
    prompt_first: bool
    smoke_tests: bool
    integration_tests: bool
    seed_data: bool
    docker_layout: bool
    include_root_readme: bool
    include_docs_dir: bool
    no_profile: bool
    force: bool
    dry_run: bool
    description: str | None = None
    prompt_files_override: dict[str, str] | None = None
    extra_profile_metadata: dict[str, object] | None = None
    extra_context_entrypoints: list[str] | None = None
    derived_context_mode: str | None = None
    extra_vendored_paths: list[str] | None = None


@dataclass(frozen=True)
class DerivedTargetPlan:
    selector_name: str
    entry: dict[str, object]
    target_dir: Path


EXAMPLE_CATEGORIES: tuple[tuple[str, range], ...] = (
    ("Category A — Single-Backend API Services", range(1, 22)),
    ("Category B — Backend-Driven UI", range(22, 28)),
    ("Category C — Data Acquisition and Pipelines", range(28, 39)),
    ("Category D — ML and Data Science", range(39, 47)),
    ("Category E — Multi-Backend Coordination", range(47, 63)),
    ("Category F — Storage Experiments", range(63, 73)),
    ("Category G — CLI Tools", range(73, 79)),
    ("Category H — Local RAG and Semantic Search", range(79, 85)),
    ("Category I — Prompt-First Repos", range(85, 91)),
    ("Category J — Dokku-Deployable Services", range(91, 99)),
    ("Additional", range(99, 101)),
)

EXAMPLE_PROJECTS: dict[int, ExampleProject] = {
    # ── Category A — Single-Backend API Services ──────────────────────────
    1: ExampleProject(
        "partner-data-enrichment",
        "FastAPI + Polars + PostgreSQL, JSON normalization, cursor pagination",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    2: ExampleProject(
        "analytics-parquet-api",
        "FastAPI analytics over DuckDB + Parquet, Polars transforms, trend and summary endpoints",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    3: ExampleProject(
        "timeseries-ingest",
        "FastAPI + TimescaleDB hypertable ingest, windowed aggregate queries",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    4: ExampleProject(
        "webhook-receiver",
        "FastAPI webhook receiver, Redis rate-limit, MongoDB document store, Polars normalize",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    5: ExampleProject(
        "scheduled-enrichment",
        "FastAPI scheduled enrichment, Polars transforms, PostgreSQL, last-run inspection endpoint",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    6: ExampleProject(
        "hono-internal-api",
        "Hono/Bun internal API, SQLite-backed domain query, health check, narrow and fast",
        "backend-api-service", "typescript-hono-bun",
        smoke_tests=True, seed_data=True,
    ),
    7: ExampleProject(
        "hono-bff-aggregator",
        "Hono/Bun BFF aggregator, upstream REST fan-in, graceful failure, Dokku-ready",
        "dokku-deployable-service", "typescript-hono-bun",
        dokku=True, smoke_tests=True, seed_data=True,
    ),
    8: ExampleProject(
        "go-parquet-reports",
        "Go/Echo Parquet report service, filter + sort + paginate JSON results",
        "backend-api-service", "go-echo",
        smoke_tests=True, seed_data=True,
    ),
    9: ExampleProject(
        "go-file-upload",
        "Go/Echo file upload service, validation + normalization + PostgreSQL write path",
        "backend-api-service", "go-echo",
        smoke_tests=True, seed_data=True,
    ),
    10: ExampleProject(
        "rust-event-ingest",
        "Rust/Axum high-throughput event ingest, batch-flush to PostgreSQL append table",
        "backend-api-service", "rust-axum-modern",
        smoke_tests=True, seed_data=True,
    ),
    11: ExampleProject(
        "rust-batch-classifier",
        "Rust/Axum batch classification service, feature vector labeling, confidence scores",
        "backend-api-service", "rust-axum-modern",
        smoke_tests=True, seed_data=True,
    ),
    12: ExampleProject(
        "phoenix-scheduling",
        "Elixir/Phoenix scheduling service, availability windows, overlap query, PostgreSQL",
        "backend-api-service", "elixir-phoenix",
        smoke_tests=True, seed_data=True,
    ),
    13: ExampleProject(
        "scala-financial-reports",
        "Scala/Tapir/ZIO financial report aggregation, period summary and comparison endpoints",
        "backend-api-service", "scala-tapir-http4s-zio",
        smoke_tests=True, seed_data=True,
    ),
    14: ExampleProject(
        "kotlin-invoice-tracker",
        "Kotlin/http4k/Exposed supplier invoice tracker, CRUD + filter-by-status, PostgreSQL",
        "backend-api-service", "kotlin-http4k-exposed",
        smoke_tests=True, seed_data=True,
    ),
    15: ExampleProject(
        "clojure-preferences",
        "Clojure/Kit user preference service, next.jdbc + PostgreSQL, one read + one write",
        "backend-api-service", "clojure-kit-nextjdbc-hiccup",
        smoke_tests=True, seed_data=True,
    ),
    16: ExampleProject(
        "ruby-content-store",
        "Ruby/Hanami content record store, paginated list, basic filtering, PostgreSQL",
        "backend-api-service", "ruby-hanami",
        smoke_tests=True, seed_data=True,
    ),
    17: ExampleProject(
        "nim-json-filter",
        "Nim/Jester fixture-backed JSON filter API, query param filtering, no live storage",
        "backend-api-service", "nim-jester-happyx",
        smoke_tests=True, seed_data=True,
    ),
    18: ExampleProject(
        "dart-audit-log",
        "Dart/Dartfrog audit log service, PostgreSQL write + paginated read, boot check",
        "backend-api-service", "dart-dartfrog",
        smoke_tests=True, seed_data=True,
    ),
    19: ExampleProject(
        "ocaml-metadata-store",
        "OCaml/Dream + Caqti/PostgreSQL metadata store, record creation and lookup, Tyxml fragments",
        "backend-api-service", "ocaml-dream-caqti-tyxml",
        smoke_tests=True, seed_data=True,
    ),
    20: ExampleProject(
        "crystal-cache-proxy",
        "Crystal/Kemal cache proxy, Avram PostgreSQL, cache-stats endpoint, smoke-tested",
        "backend-api-service", "crystal-kemal-avram",
        smoke_tests=True, seed_data=True,
    ),
    21: ExampleProject(
        "fastapi-dokku-analytics",
        "FastAPI analytics + Dokku, Polars CSV ingest, PostgreSQL, ingest + summary endpoints",
        "dokku-deployable-service", "python-fastapi-uv-ruff-orjson-polars",
        dokku=True, smoke_tests=True, seed_data=True,
    ),
    # ── Category B — Backend-Driven UI ───────────────────────────────────
    22: ExampleProject(
        "faceted-dashboard",
        "FastAPI + HTMX faceted dashboard, Plotly chart, Tailwind, Playwright fragment tests",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, integration_tests=True, seed_data=True,
    ),
    23: ExampleProject(
        "search-sort-paginate",
        "FastAPI + HTMX search/sort/paginate UI, keyword search, three-field sort, Playwright CUJ",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, integration_tests=True, seed_data=True,
    ),
    24: ExampleProject(
        "split-filter-panel",
        "FastAPI + HTMX split filter panel, server-side state, include/exclude facets, Playwright",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, integration_tests=True, seed_data=True,
    ),
    25: ExampleProject(
        "shared-query-chart-table",
        "FastAPI shared query for Plotly chart + table, HTMX fragment swap, Playwright verified",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, integration_tests=True, seed_data=True,
    ),
    26: ExampleProject(
        "report-browser-cuj",
        "FastAPI report browser, HTMX + Tailwind, five CUJ Playwright tests, filter/sort/export",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, integration_tests=True, seed_data=True,
    ),
    27: ExampleProject(
        "compound-facet-dashboard",
        "FastAPI compound facet dashboard, AND-logic multi-dimension filter, Playwright count tests",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, integration_tests=True, seed_data=True,
    ),
    # ── Category C — Data Acquisition and Pipelines ───────────────────────
    28: ExampleProject(
        "python-api-acquisition",
        "Python data acquisition, paginated REST API, raw JSON archive, PostgreSQL sync state",
        "data-acquisition-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    29: ExampleProject(
        "go-api-ingestion",
        "Go API ingestion, external JSON API, archive + normalize + PostgreSQL, retry with backoff",
        "data-acquisition-service", "go-echo",
        smoke_tests=True, seed_data=True,
    ),
    30: ExampleProject(
        "python-scraper",
        "Python HTML scraper, Polars normalize, raw HTML archive, PostgreSQL, fixture parser tests",
        "data-acquisition-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    31: ExampleProject(
        "bun-scraper",
        "TypeScript/Bun HTML scraper, Drizzle PostgreSQL write, fixture-based parser tests",
        "data-acquisition-service", "typescript-hono-bun",
        smoke_tests=True, seed_data=True,
    ),
    32: ExampleProject(
        "csv-etl-pipeline",
        "Python CSV ETL pipeline, Polars transforms, Parquet output, fixture-based verification",
        "data-pipeline", "duckdb-trino-polars",
        smoke_tests=True, seed_data=True,
    ),
    33: ExampleProject(
        "json-etl-pipeline",
        "Python JSON ETL pipeline, Polars enrich + validate, PostgreSQL bulk insert, fixture tests",
        "data-pipeline", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    34: ExampleProject(
        "duckdb-parquet-analytics",
        "DuckDB + Parquet local analytics pipeline, CSV ingest, SQL queries, no cloud deps",
        "data-pipeline", "duckdb-trino-polars",
        smoke_tests=True, seed_data=True,
    ),
    35: ExampleProject(
        "multi-source-sync",
        "Python multi-source sync platform, NATS JetStream events, two sources, coordinator",
        "multi-source-sync-platform", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    36: ExampleProject(
        "classification-enrichment",
        "Python classification enrichment, PostgreSQL input, classifier tag + confidence, provenance",
        "data-acquisition-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    37: ExampleProject(
        "recurring-sync",
        "Python recurring sync service, configurable schedule, backoff + jitter, archive + metadata",
        "data-acquisition-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    38: ExampleProject(
        "elixir-data-acquisition",
        "Elixir data acquisition, GenServer polling, raw JSON archive, Ecto normalize, PostgreSQL",
        "data-acquisition-service", "elixir-phoenix",
        smoke_tests=True, seed_data=True,
    ),
    # ── Category D — ML and Data Science ─────────────────────────────────
    39: ExampleProject(
        "sklearn-inference",
        "FastAPI scikit-learn inference service, persisted model, predict endpoint, fixture smoke tests",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    40: ExampleProject(
        "recommendation-engine",
        "FastAPI recommendation endpoint, Polars + PostgreSQL pre-computed table, ranked list",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    41: ExampleProject(
        "arima-forecasting",
        "FastAPI ARIMA forecasting service, statsmodels, multi-step forecast, confidence intervals",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    42: ExampleProject(
        "semantic-search-qdrant",
        "FastAPI semantic search, sentence-transformers + Qdrant, fixture corpus smoke test",
        "local-rag-system", "qdrant",
        smoke_tests=True, seed_data=True,
    ),
    43: ExampleProject(
        "xgboost-serving",
        "FastAPI XGBoost serving, persisted model, feature importance metadata, fixture smoke test",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    44: ExampleProject(
        "embedding-pipeline",
        "Python embedding pipeline, sentence-transformers + Qdrant upsert, FastAPI query endpoint",
        "local-rag-system", "qdrant",
        smoke_tests=True, seed_data=True,
    ),
    45: ExampleProject(
        "duckdb-polars-sklearn",
        "DuckDB + Polars + scikit-learn pipeline, Parquet feature sets, classification report",
        "data-pipeline", "duckdb-trino-polars",
        smoke_tests=True, seed_data=True,
    ),
    46: ExampleProject(
        "lightgbm-tabular",
        "LightGBM tabular pipeline, Polars feature engineering, Parquet training data, eval metrics",
        "data-pipeline", "duckdb-trino-polars",
        smoke_tests=True, seed_data=True,
    ),
    # ── Category E — Multi-Backend Coordination ───────────────────────────
    47: ExampleProject(
        "go-python-ml-gateway",
        "Go/Echo gateway + FastAPI Python ML scoring, REST seam, docker-compose end-to-end",
        "multi-backend-service", "go-echo",
        smoke_tests=True, seed_data=True,
    ),
    48: ExampleProject(
        "kotlin-rust-grpc",
        "Kotlin/http4k caller + Rust/Tonic gRPC server, .proto seam, docker-compose verified",
        "multi-backend-service", "kotlin-http4k-exposed",
        smoke_tests=True,
    ),
    49: ExampleProject(
        "elixir-go-nats",
        "Elixir NATS publisher + Go JetStream consumer, fan-out, subject structure, ACK demo",
        "multi-backend-service", "elixir-phoenix",
        smoke_tests=True,
    ),
    50: ExampleProject(
        "clojure-go-kafka",
        "Clojure Kafka producer + Go Kafka consumer, correlation ID enrichment, docker-compose",
        "multi-backend-service", "clojure-kit-nextjdbc-hiccup",
        smoke_tests=True,
    ),
    51: ExampleProject(
        "node-go-graphql",
        "Node/Hono GraphQL BFF + Go/Echo domain REST API, resolver + HTTP client mapping",
        "multi-backend-service", "typescript-hono-bun",
        smoke_tests=True,
    ),
    52: ExampleProject(
        "scala-rust-grpc-streams",
        "Scala/Akka Streams pipeline + Rust/Tonic gRPC compute kernel, docker-compose",
        "multi-backend-service", "scala-tapir-http4s-zio",
        smoke_tests=True,
    ),
    53: ExampleProject(
        "node-elixir-nats-bidir",
        "Node NATS publisher + Elixir NATS subscriber, bidirectional event seam, docker-compose",
        "multi-backend-service", "typescript-hono-bun",
        smoke_tests=True,
    ),
    54: ExampleProject(
        "rust-python-grpc-infer",
        "Rust/Tonic gRPC inference server + Python orchestrator, batch features, docker-compose",
        "multi-backend-service", "rust-axum-modern",
        smoke_tests=True,
    ),
    55: ExampleProject(
        "elixir-rust-nif",
        "Elixir + Rust NIF via Rustler, in-process compute function, no docker-compose",
        "multi-backend-service", "elixir-phoenix",
        smoke_tests=True,
    ),
    56: ExampleProject(
        "elixir-clojure-rabbitmq",
        "Elixir RabbitMQ producer + Clojure Broadway consumer, work queue, docker-compose",
        "multi-backend-service", "elixir-phoenix",
        smoke_tests=True,
    ),
    57: ExampleProject(
        "trio-go-elixir-python",
        "Go gateway + Elixir NATS coordinator + Python ML REST service, three-service docker-compose",
        "multi-backend-service", "go-echo",
        smoke_tests=True,
    ),
    58: ExampleProject(
        "trio-go-rust-python-dual",
        "Go gateway + Rust gRPC kernel + Python REST scoring, two seam types, docker-compose",
        "multi-backend-service", "go-echo",
        smoke_tests=True,
    ),
    59: ExampleProject(
        "trio-elixir-go-rust-nats",
        "Elixir coordinator + Go NATS worker + Rust gRPC kernel, supervision + fault tolerance",
        "multi-backend-service", "elixir-phoenix",
        smoke_tests=True,
    ),
    60: ExampleProject(
        "trio-node-go-python-gql",
        "Node GraphQL BFF + Go domain REST + Python ML REST, GraphQL schema stitching",
        "multi-backend-service", "typescript-hono-bun",
        smoke_tests=True,
    ),
    61: ExampleProject(
        "trio-rust-nats-go-iot",
        "Rust IoT ingestor + NATS JetStream + Go windowed aggregator REST endpoint",
        "multi-backend-service", "rust-axum-modern",
        smoke_tests=True,
    ),
    62: ExampleProject(
        "scala-go-python-federated",
        "Scala/gRPC + Go analytics worker + Python data layer REST, federated analytics",
        "multi-backend-service", "scala-tapir-http4s-zio",
        smoke_tests=True,
    ),
    # ── Category F — Storage Experiments ─────────────────────────────────
    63: ExampleProject(
        "duckdb-parquet-minio-lake",
        "DuckDB + Parquet + MinIO local data lake, S3-compatible query, docker-compose",
        "data-pipeline", "duckdb-trino-polars",
        smoke_tests=True, seed_data=True,
    ),
    64: ExampleProject(
        "rag-engineering-runbooks",
        "Local RAG for engineering runbooks, Qdrant + sentence-transformers, fixture corpus",
        "local-rag-system", "qdrant",
        smoke_tests=True, seed_data=True,
    ),
    65: ExampleProject(
        "meilisearch-fulltext",
        "FastAPI + Meilisearch full-text search, attribute ranking, fixture data, smoke tests",
        "multi-storage-experiment", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    66: ExampleProject(
        "timescaledb-sensors",
        "FastAPI + TimescaleDB sensor ingest, hypertable, hourly + daily aggregate endpoints",
        "backend-api-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    67: ExampleProject(
        "redis-cache-ratelimit",
        "FastAPI + Redis caching layer + rate limiter, cache hit/miss and rejection verified",
        "multi-storage-experiment", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    68: ExampleProject(
        "nats-event-capture-replay",
        "NATS JetStream event capture + replay experiment, stream config, publish/subscribe",
        "multi-storage-experiment", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    69: ExampleProject(
        "trino-federated-query",
        "Trino federated query, PostgreSQL + Parquet catalogs, FastAPI cross-catalog endpoint",
        "data-pipeline", "duckdb-trino-polars",
        smoke_tests=True, seed_data=True,
    ),
    70: ExampleProject(
        "multi-storage-split",
        "Redis hot cache + MongoDB document store + Parquet batch export, storage split",
        "multi-storage-experiment", "redis-keydb-mongo",
        smoke_tests=True, seed_data=True,
    ),
    71: ExampleProject(
        "elasticsearch-search",
        "FastAPI + Elasticsearch search, relevance scoring + field filtering, fixture corpus",
        "multi-storage-experiment", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    72: ExampleProject(
        "es-vs-meilisearch",
        "Elasticsearch vs Meilisearch side-by-side comparison, same corpus, timing metadata",
        "multi-storage-experiment", "redis-keydb-mongo",
        smoke_tests=True, seed_data=True,
    ),
    # ── Category G — CLI Tools ────────────────────────────────────────────
    73: ExampleProject(
        "data-reconciliation-cli",
        "Python CLI data reconciliation, structured diff report, two-file key comparison",
        "cli-tool", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    74: ExampleProject(
        "prompt-eval-cli",
        "Python CLI prompt evaluator, YAML rubric, fixture dataset, structured comparison report",
        "cli-tool", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    75: ExampleProject(
        "rust-batch-processor",
        "Rust CLI batch processor, directory input, validation + normalization, snapshot tests",
        "cli-tool", "rust-axum-modern",
        smoke_tests=True, seed_data=True,
    ),
    76: ExampleProject(
        "rust-snapshot-cli",
        "Rust CLI snapshot test harness, structured JSON output, fixture-driven exact verification",
        "cli-tool", "rust-axum-modern",
        smoke_tests=True, seed_data=True,
    ),
    77: ExampleProject(
        "go-config-auditor",
        "Go CLI config auditor, YAML policy rules, directory config scan, findings report",
        "cli-tool", "go-echo",
        smoke_tests=True, seed_data=True,
    ),
    78: ExampleProject(
        "python-pipeline-cli",
        "Python CLI data acquisition wrapper, sync/inspect/replay subcommands, sync state tracking",
        "cli-tool", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True, seed_data=True,
    ),
    # ── Category H — Local RAG and Semantic Search ────────────────────────
    79: ExampleProject(
        "rag-legal-docs",
        "Local RAG for legal documents, Qdrant + sentence-transformers, metadata excerpts",
        "local-rag-system", "qdrant",
        smoke_tests=True, seed_data=True,
    ),
    80: ExampleProject(
        "rag-api-reference",
        "Local RAG for API reference docs, Qdrant + metadata (endpoint/method/desc), fixture corpus",
        "local-rag-system", "qdrant",
        smoke_tests=True, seed_data=True,
    ),
    81: ExampleProject(
        "markdown-notes-indexer",
        "Markdown notes indexer, section chunking, sentence-transformers + Qdrant, source metadata",
        "local-rag-system", "qdrant",
        smoke_tests=True, seed_data=True,
    ),
    82: ExampleProject(
        "runbook-search",
        "Policy and runbook search, Qdrant intent query, most relevant step + context",
        "local-rag-system", "qdrant",
        smoke_tests=True, seed_data=True,
    ),
    83: ExampleProject(
        "hybrid-search-prototype",
        "Hybrid search: Meilisearch full-text + Qdrant semantic, weighted rank fusion, unified list",
        "local-rag-system", "qdrant",
        smoke_tests=True, seed_data=True,
    ),
    84: ExampleProject(
        "rag-plus-structured",
        "RAG-supplemented structured query, Qdrant context chunks + structured result, fixture corpus",
        "local-rag-system", "qdrant",
        smoke_tests=True, seed_data=True,
    ),
    # ── Category I — Prompt-First Repos ──────────────────────────────────
    85: ExampleProject(
        "prompt-rubric-evaluator",
        "Prompt-first repo: YAML rubric evaluator, scored evaluation reports, monotonic prompt files",
        "prompt-first-repo", "prompt-first-repo",
    ),
    86: ExampleProject(
        "output-shape-compliance",
        "Prompt-first repo: output shape compliance, JSON schema assertions, fixture-based harness",
        "prompt-first-repo", "prompt-first-repo",
    ),
    87: ExampleProject(
        "prompt-assertion-library",
        "Prompt-first system prompt library, output assertion set, single harness run",
        "prompt-first-repo", "prompt-first-repo",
    ),
    88: ExampleProject(
        "model-config-comparison",
        "Prompt-first model config comparison, multi-config output comparison, structured report",
        "prompt-first-repo", "prompt-first-repo",
    ),
    89: ExampleProject(
        "task-prompt-sequences",
        "Prompt-first task prompt sequences, monotonic numbering, output shapes + continuations",
        "prompt-first-repo", "prompt-first-repo",
    ),
    90: ExampleProject(
        "living-doc-prompts",
        "Prompt-first living doc repo, documentation fragment generation + structure verification",
        "prompt-first-repo", "prompt-first-repo",
    ),
    # ── Category J — Dokku-Deployable Services ────────────────────────────
    91: ExampleProject(
        "dokku-fastapi-analytics",
        "FastAPI analytics + Dokku, PostgreSQL aggregate endpoint, Procfile + app.json",
        "dokku-deployable-service", "python-fastapi-uv-ruff-orjson-polars",
        dokku=True, smoke_tests=True, seed_data=True,
    ),
    92: ExampleProject(
        "dokku-fastapi-redis-cache",
        "FastAPI + Redis caching + Dokku, cache-hit/miss paths, Dokku Redis plugin notes",
        "dokku-deployable-service", "python-fastapi-uv-ruff-orjson-polars",
        dokku=True, smoke_tests=True, seed_data=True,
    ),
    93: ExampleProject(
        "dokku-hono-bun",
        "Hono/Bun + Dokku, health check + domain query, Procfile, env var discipline",
        "dokku-deployable-service", "typescript-hono-bun",
        dokku=True, smoke_tests=True, seed_data=True,
    ),
    94: ExampleProject(
        "dokku-go-echo",
        "Go/Echo + PostgreSQL + Dokku, health + reporting route, Procfile + go.mod",
        "dokku-deployable-service", "go-echo",
        dokku=True, smoke_tests=True, seed_data=True,
    ),
    95: ExampleProject(
        "dokku-phoenix",
        "Elixir/Phoenix + Dokku, one API route + server-rendered view, Ecto + Procfile",
        "dokku-deployable-service", "elixir-phoenix",
        dokku=True, smoke_tests=True, seed_data=True,
    ),
    96: ExampleProject(
        "dokku-multi-service",
        "FastAPI + Hono/Bun multi-service Dokku deploy, shared PostgreSQL, service isolation",
        "dokku-deployable-service", "python-fastapi-uv-ruff-orjson-polars",
        dokku=True, smoke_tests=True, seed_data=True,
    ),
    97: ExampleProject(
        "dokku-rust-axum",
        "Rust/Axum + Dokku, health + domain route, Procfile + Docker build stage",
        "dokku-deployable-service", "rust-axum-modern",
        dokku=True, smoke_tests=True, seed_data=True,
    ),
    98: ExampleProject(
        "dokku-kotlin-http4k",
        "Kotlin/http4k + PostgreSQL + Dokku, reporting route, Procfile + JVM config",
        "dokku-deployable-service", "kotlin-http4k-exposed",
        dokku=True, smoke_tests=True, seed_data=True,
    ),
    # ── Additional ────────────────────────────────────────────────────────
    99: ExampleProject(
        "crystal-data-acquisition",
        "Crystal/Kemal data acquisition, Avram PostgreSQL, archive + normalize, fixture smoke tests",
        "data-acquisition-service", "crystal-kemal-avram",
        smoke_tests=True, seed_data=True,
    ),
    100: ExampleProject(
        "polyglot-seam-lab",
        "Polyglot seam lab, two-or-three-language coordination, broker or REST seam, round-trip demo",
        "multi-backend-service", "python-fastapi-uv-ruff-orjson-polars",
        smoke_tests=True,
    ),
}

DERIVED_COLLECTION_SELECTORS = {
    "team-a": "A",
    "team-b": "B",
    "all-derived": "*",
}

DERIVED_CONTEXT_MODES = ("compact", "maximal")

# Maximal derived repos intentionally vendor more than the manifest-linked compact
# bundle. Keep the extra copy policy named and centralized so generation behavior,
# metadata, prompts, and tests all describe the same bounded surface.
DERIVED_MAXIMAL_BUNDLE_POLICY_NAME = "derived-maximal-prompt-first-continuation-v1"
DERIVED_MAXIMAL_BUNDLE_POLICY_NOTE = (
    "Maximal mode vendors a bounded repo-local continuation bundle so a fresh "
    "assistant session can continue prompt-first work without reopening the "
    "source generator repo. Compact mode still vendors only the selected base "
    "manifests plus their linked support assets."
)
DERIVED_MAXIMAL_BUNDLE_POLICY_SECTIONS = (
    {
        "name": "prompt-first-routing-supplements",
        "category": "routing-and-doctrine",
        "authority": "authoritative",
        "startup_priority": "startup",
        "paths": (
            "context/anchors/prompt-first.md",
            "context/anchors/session-start.md",
            "context/anchors/repo-identity.md",
            "context/anchors/context-loading-principles.md",
            "context/anchors/context-integrity.md",
            "context/doctrine/canonical-examples.md",
            "context/doctrine/commit-hygiene.md",
            "context/doctrine/naming-and-clarity.md",
            "context/doctrine/stop-conditions.md",
            "context/workflows/generate-prompt-sequence.md",
            "context/workflows/post-flight-refinement.md",
            "context/skills/canonical-example-selection.md",
            "context/skills/context-bundle-assembly.md",
            "context/skills/manifest-selection.md",
            "context/skills/memory-continuity-discipline.md",
            "context/skills/verification-path-selection.md",
        ),
        "why": "Prompt-first doctrine, routing, and continuation helpers not guaranteed by manifest-linked compact vendoring.",
    },
    {
        "name": "canonical-examples",
        "category": "canonical-examples",
        "authority": "informative",
        "startup_priority": "startup",
        "paths": (
            "examples/canonical-prompts/README.md",
            "examples/canonical-prompts/prompt-first-layout-example.md",
            "examples/canonical-prompts/001-bootstrap-repo.txt",
            "examples/canonical-prompts/002-refine-test-surface.txt",
            "examples/canonical-workflows/README.md",
            "examples/canonical-workflows/HANDOFF-SNAPSHOT.example.md",
            "examples/canonical-workflows/MEMORY.example.md",
        ),
        "why": "Canonical prompt and workflow examples let the derived repo extend `.prompts/` confidently from repo-local precedents.",
    },
    {
        "name": "prompt-continuation-templates",
        "category": "templates",
        "authority": "templating-reference",
        "startup_priority": "supporting",
        "paths": (
            "templates/manifest/manifest.template.yaml",
            "templates/prompt-first/PROMPTS.md.template",
            "templates/prompt-first/001-bootstrap.template.txt",
            "templates/prompt-first/002-refine.template.txt",
        ),
        "why": "Template references help continuation work stay aligned with prompt-first repo conventions without turning templates into live state.",
    },
)


DEFAULT_MANIFESTS = {
    ("backend-api-service", "python-fastapi-uv-ruff-orjson-polars"): ["backend-api-fastapi-polars"],
    ("backend-api-service", "typescript-hono-bun"): ["backend-api-typescript-hono-bun"],
    ("backend-api-service", "rust-axum-modern"): ["backend-api-rust-axum"],
    ("backend-api-service", "kotlin-http4k-exposed"): ["backend-api-kotlin-http4k-exposed"],
    ("backend-api-service", "zig-zap-jetzig"): ["backend-api-zig-zap-jetzig"],
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
    ("backend-api-service", "nim-jester-happyx"): ["backend-api-nim-jester-happyx"],
    ("backend-api-service", "scala-tapir-http4s-zio"): ["backend-api-scala-tapir-http4s-zio"],
    ("backend-api-service", "clojure-kit-nextjdbc-hiccup"): ["backend-api-clojure-kit-nextjdbc-hiccup"],
    ("backend-api-service", "dart-dartfrog"): ["backend-api-dart-dartfrog"],
    ("data-acquisition-service", "python-fastapi-uv-ruff-orjson-polars"): ["data-acquisition-service"],
    ("multi-source-sync-platform", "python-fastapi-uv-ruff-orjson-polars"): ["multi-source-sync-platform"],
    ("backend-api-service", "crystal-kemal-avram"): ["backend-api-crystal-kemal-avram"],
    ("backend-api-service", "ruby-hanami"): ["backend-api-ruby-hanami"],
    ("backend-api-service", "ocaml-dream-caqti-tyxml"): ["backend-api-ocaml-dream-caqti-tyxml"],
    ("data-acquisition-service", "crystal-kemal-avram"): ["backend-api-crystal-kemal-avram"],
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


def _coerce_int_list(value: object) -> list[int]:
    """Return a list of ints from either a list or an inline '[1, 2, 3]' string."""
    if isinstance(value, list):
        return [int(x) for x in value]
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            if not inner:
                return []
            return [int(x.strip()) for x in inner.split(",")]
    return []


def _coerce_str_list(value: object) -> list[str]:
    """Return a list of strings from either a list or an inline YAML list string."""

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("[") and text.endswith("]"):
            inner = text[1:-1].strip()
            if not inner:
                return []
            return [part.strip().strip("'\"") for part in inner.split(",") if part.strip()]
        return [text]
    return []


def _parse_simple_yaml_scalar(raw: str) -> object:
    """Parse the limited scalar shapes used by examples/derived/*.yaml."""

    value = raw.strip()
    if not value:
        return ""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        parsed = ast.literal_eval(value)
        return list(parsed) if isinstance(parsed, tuple) else parsed
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return ast.literal_eval(value)
    return value


def _collect_block_scalar(lines: list[str], start: int, parent_indent: int) -> tuple[str, int]:
    """Collect YAML block-scalar text preserving its real multiline content."""

    index = start
    content: list[str] = []
    block_indent: int | None = None
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        current_indent = len(raw_line) - len(raw_line.lstrip(" "))
        if stripped and current_indent <= parent_indent:
            break
        if stripped:
            if block_indent is None:
                block_indent = current_indent
            content.append(raw_line[block_indent:])
        else:
            content.append("")
        index += 1
    while content and not content[-1]:
        content.pop()
    return "\n".join(content), index


def _parse_yaml_mapping_block(lines: list[str], start: int, indent: int) -> tuple[dict[str, object], int]:
    """Parse an indented YAML mapping block with optional block scalars."""

    mapping: dict[str, object] = {}
    index = start
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        current_indent = len(raw_line) - len(raw_line.lstrip(" "))
        if current_indent < indent:
            break
        if current_indent != indent:
            raise ValueError(f"unexpected indentation in {raw_line!r}")
        if ":" not in stripped:
            raise ValueError(f"expected mapping entry in {raw_line!r}")
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        index += 1
        if raw_value == "|":
            value, index = _collect_block_scalar(lines, index, current_indent)
            mapping[key] = value
            continue
        if raw_value:
            mapping[key] = _parse_simple_yaml_scalar(raw_value)
            continue
        nested, index = _parse_yaml_sequence_of_mappings(lines, index, current_indent + 2)
        mapping[key] = nested
    return mapping, index


def _parse_yaml_sequence_of_mappings(
    lines: list[str], start: int, indent: int
) -> tuple[list[dict[str, object]], int]:
    """Parse a YAML sequence where each item is a mapping."""

    items: list[dict[str, object]] = []
    index = start
    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        current_indent = len(raw_line) - len(raw_line.lstrip(" "))
        if current_indent < indent:
            break
        if current_indent != indent or not stripped.startswith("- "):
            raise ValueError(f"expected sequence entry in {raw_line!r}")
        item_text = stripped[2:].strip()
        item: dict[str, object] = {}
        if item_text:
            if ":" not in item_text:
                raise ValueError(f"expected mapping item in {raw_line!r}")
            key, raw_value = item_text.split(":", 1)
            key = key.strip()
            raw_value = raw_value.strip()
            index += 1
            if raw_value == "|":
                value, index = _collect_block_scalar(lines, index, current_indent)
                item[key] = value
            elif raw_value:
                item[key] = _parse_simple_yaml_scalar(raw_value)
            else:
                nested, index = _parse_yaml_sequence_of_mappings(lines, index, current_indent + 2)
                item[key] = nested
        else:
            index += 1
        nested_fields, index = _parse_yaml_mapping_block(lines, index, current_indent + 2)
        item.update(nested_fields)
        items.append(item)
    return items, index


def _load_yaml_with_block_scalars_from_path(path: Path) -> object:
    """Load the limited YAML shapes used in examples/derived/*.yaml."""

    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        if ":" not in stripped:
            raise ValueError(f"{path}: expected top-level mapping key")
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value:
            return {key: _parse_simple_yaml_scalar(raw_value)}
        parsed, _ = _parse_yaml_sequence_of_mappings(lines, index + 1, 2)
        return {key: parsed}
    return {}


def _load_derived_data() -> dict[str, list[dict]]:
    """Load derived-examples.yaml and spin-outs.yaml from examples/derived/.

    Returns {"derived": [...], "spin_outs": [...]}.
    Returns empty lists for any file that does not exist yet (run PROMPT_76/78 first).
    Uses the repo's custom YAML parser with block scalar support (no PyYAML dependency).
    """
    repo_root = Path(__file__).resolve().parent.parent
    derived_dir = repo_root / "examples" / "derived"

    derived: list[dict] = []
    spin_outs: list[dict] = []
    de_path = derived_dir / "derived-examples.yaml"
    if de_path.exists():
        raw = _load_yaml_with_block_scalars_from_path(de_path)
        derived = raw.get("derived", []) if isinstance(raw, dict) else []
    so_path = derived_dir / "spin-outs.yaml"
    if so_path.exists():
        raw = _load_yaml_with_block_scalars_from_path(so_path)
        spin_outs = raw.get("spin_outs", []) if isinstance(raw, dict) else []
    return {"derived": derived, "spin_outs": spin_outs}


def _find_derived_leaf_entry(name: str, data: dict[str, list[dict]]) -> dict[str, object] | None:
    """Return one derived leaf entry by name."""

    return next((entry for entry in data["derived"] if entry.get("name") == name), None)


def _expand_derived_selector(name: str, data: dict[str, list[dict]]) -> list[dict[str, object]]:
    """Expand a derived selector into one or more derived leaf entries."""

    if name in DERIVED_COLLECTION_SELECTORS:
        team = DERIVED_COLLECTION_SELECTORS[name]
        if team == "*":
            return list(data["derived"])
        return [entry for entry in data["derived"] if entry.get("team") == team]
    entry = _find_derived_leaf_entry(name, data)
    return [entry] if entry is not None else []


def _normalize_resolved_path(path: Path) -> Path:
    """Resolve a path while treating /tmp and /private/tmp equivalently on macOS."""

    return path.expanduser().resolve()


def _resolve_leaf_target(selector_name: str, target_dir: str | None) -> Path:
    """Resolve the final target path for one derived leaf repo."""

    if target_dir is None:
        return _normalize_resolved_path(Path.cwd() / selector_name)
    requested = _normalize_resolved_path(Path(target_dir))
    if requested.exists() and requested.is_dir():
        return _normalize_resolved_path(requested / selector_name)
    return requested


def _resolve_team_parent(target_dir: str | None) -> Path:
    """Resolve the parent directory used by a collection selector."""

    if target_dir is None:
        return _normalize_resolved_path(Path.cwd())
    return _normalize_resolved_path(Path(target_dir))


def _resolve_derived_targets(
    selector_name: str,
    entries: list[dict[str, object]],
    target_dir: str | None,
) -> list[DerivedTargetPlan]:
    """Resolve exact target directories for all derived leaf repos."""

    if not entries:
        return []
    if selector_name in DERIVED_COLLECTION_SELECTORS:
        parent = _resolve_team_parent(target_dir)
        return [
            DerivedTargetPlan(
                selector_name=selector_name,
                entry=entry,
                target_dir=_normalize_resolved_path(parent / str(entry["name"])),
            )
            for entry in entries
        ]
    entry = entries[0]
    return [
        DerivedTargetPlan(
            selector_name=selector_name,
            entry=entry,
            target_dir=_resolve_leaf_target(str(entry["name"]), target_dir),
        )
    ]


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
        "--include-root-readme",
        action="store_true",
        help="Generate a root README.md now instead of deferring front-facing docs.",
    )
    parser.add_argument(
        "--include-docs-dir",
        action="store_true",
        help="Generate a root docs/ directory now instead of deferring it.",
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
    parser.add_argument(
        "--list-derived",
        action="store_true",
        help="Print all derived examples (sub-groups and spin-out platforms) and exit.",
    )
    parser.add_argument(
        "--derived-example",
        metavar="NAME",
        help="Print the cluster guide for a derived example or spin-out by name and exit.",
    )
    parser.add_argument(
        "--derived-context-mode",
        choices=DERIVED_CONTEXT_MODES,
        default="compact",
        help="Derived generation vendoring mode. Default: compact.",
    )
    parser.add_argument(
        "--list-examples",
        action="store_true",
        help="Print all 100 reference project examples grouped by category and exit.",
    )
    parser.add_argument(
        "--use-example",
        type=int,
        metavar="N",
        help="Pre-fill archetype, stack, and flags from reference project N (1-100). "
             "repo_name defaults to NNN-codename unless supplied explicitly.",
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


def load_manifest_texts(selected_manifests: list[str]) -> dict[str, str]:
    """Load raw manifest snapshots for vendoring into generated repos."""

    manifest_dir = repo_root() / "manifests"
    manifest_texts: dict[str, str] = {}
    for manifest_name in selected_manifests:
        path = manifest_dir / f"{manifest_name}.yaml"
        if not path.exists():
            raise ValueError(f"Unknown manifest: {manifest_name}")
        manifest_texts[manifest_name] = path.read_text(encoding="utf-8")
    return manifest_texts


def _manifest_support_asset_paths(
    selected_manifests: list[str],
    manifests: dict[str, dict[str, object]],
) -> list[str]:
    """Return manifest-linked repo-relative asset paths to vendor."""

    keys = (
        "required_context",
        "optional_context",
        "preferred_examples",
        "recommended_templates",
    )
    paths: list[str] = []
    for manifest_name in selected_manifests:
        manifest = manifests[manifest_name]
        for key in keys:
            value = manifest.get(key, [])
            if not isinstance(value, list):
                continue
            for item in value:
                path = str(item).strip()
                if not path or path in paths:
                    continue
                full_path = repo_root() / path
                if full_path.is_file():
                    paths.append(path)
    return paths


def load_manifest_support_asset_texts(
    selected_manifests: list[str],
    manifests: dict[str, dict[str, object]],
) -> dict[str, str]:
    """Load manifest-linked support assets for vendoring into generated repos."""

    asset_texts: dict[str, str] = {}
    for relative_path in _manifest_support_asset_paths(selected_manifests, manifests):
        asset_texts[relative_path] = (repo_root() / relative_path).read_text(encoding="utf-8")
    return asset_texts


def _dedupe_existing_repo_paths(paths: list[str]) -> list[str]:
    """Return existing repo-relative file paths in first-seen order."""

    seen: set[str] = set()
    filtered: list[str] = []
    for path in paths:
        normalized = path.strip()
        if not normalized or normalized in seen:
            continue
        if (repo_root() / normalized).is_file():
            seen.add(normalized)
            filtered.append(normalized)
    return filtered


def _derived_maximal_bundle_paths(
    entry: dict[str, object],
    selected_manifests: list[str],
    manifests: dict[str, dict[str, object]],
) -> list[str]:
    """Return the additional bounded support bundle for maximal derived repos."""

    compact_paths = set(_manifest_support_asset_paths(selected_manifests, manifests))
    source_specs = _source_example_specs_for_derived(entry)
    source_context_paths: list[str] = []
    for item in source_specs:
        source_context_paths.extend(
            [
                f"context/archetypes/{item['archetype']}.md",
                f"context/stacks/{item['primary_stack']}.md",
            ]
        )

    candidate_paths = _dedupe_existing_repo_paths(
        [
            *[
                path
                for section in DERIVED_MAXIMAL_BUNDLE_POLICY_SECTIONS
                for path in section["paths"]
            ],
            *source_context_paths,
        ]
    )
    return [path for path in candidate_paths if path not in compact_paths]


def _derived_maximal_bundle_records(
    entry: dict[str, object],
    selected_manifests: list[str],
    manifests: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    """Describe the extra bounded support bundle for maximal derived repos."""

    mode_paths = set(_derived_maximal_bundle_paths(entry, selected_manifests, manifests))
    records: list[dict[str, object]] = []
    for section in DERIVED_MAXIMAL_BUNDLE_POLICY_SECTIONS:
        for path in section["paths"]:
            if path in mode_paths:
                records.append(
                    {
                        "path": path,
                        "section": section["name"],
                        "category": section["category"],
                        "authority": section["authority"],
                        "startup_priority": section["startup_priority"],
                        "why": section["why"],
                        "added_by_mode": "maximal",
                    }
                )
    for path in _dedupe_existing_repo_paths(
        [
            f"context/archetypes/{item['archetype']}.md"
            for item in _source_example_specs_for_derived(entry)
        ]
        + [
            f"context/stacks/{item['primary_stack']}.md"
            for item in _source_example_specs_for_derived(entry)
        ]
    ):
        if path in mode_paths:
            records.append(
                {
                    "path": path,
                    "section": "source-example-shape-docs",
                    "category": "source-example-shape",
                    "authority": "authoritative",
                    "startup_priority": "supporting",
                    "why": "Source-example archetype and stack docs preserve the local shape lineage for the derived scenario.",
                    "added_by_mode": "maximal",
                }
            )
    return records


def _derived_maximal_startup_paths(bundle_records: list[dict[str, object]]) -> list[str]:
    """Return the startup-focused maximal bundle subset in stable order."""

    return [
        str(record["path"])
        for record in bundle_records
        if record["startup_priority"] == "startup"
    ]


def _derived_manifest_startup_paths(
    selected_manifests: list[str],
    manifests: dict[str, dict[str, object]],
) -> list[str]:
    """Return the vendored manifest-linked files that should be surfaced first."""

    startup_paths: list[str] = []
    for manifest_name in selected_manifests:
        manifest = manifests[manifest_name]
        startup_paths.extend(_coerce_str_list(manifest.get("required_context")))
        startup_paths.extend(
            path
            for path in _coerce_str_list(manifest.get("optional_context"))
            if path.startswith("context/workflows/")
        )
        startup_paths.extend(_coerce_str_list(manifest.get("preferred_examples")))
    return _dedupe_existing_repo_paths(startup_paths)


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
    if primary_stack in {
        "typescript-hono-bun",
        "rust-axum-modern",
        "kotlin-http4k-exposed",
        "zig-zap-jetzig",
        "go-echo",
        "elixir-phoenix",
        "nim-jester-happyx",
        "scala-tapir-http4s-zio",
        "clojure-kit-nextjdbc-hiccup",
        "dart-dartfrog",
        "crystal-kemal-avram",
        "ruby-hanami",
        "ocaml-dream-caqti-tyxml",
    }:
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


def validate_target(target_dir: Path, force: bool) -> None:
    """Validate that the target directory can be written without creating it yet."""

    if target_dir.exists():
        if not target_dir.is_dir():
            raise ValueError(f"Target path '{target_dir}' exists and is not a directory.")
        if any(target_dir.iterdir()) and not force:
            raise ValueError(
                f"Target directory '{target_dir}' already exists and is not empty. Use --force to continue."
            )
        return
    parent = target_dir.parent
    while not parent.exists() and parent != parent.parent:
        parent = parent.parent
    if parent.exists() and not parent.is_dir():
        raise ValueError(f"Parent path '{parent}' exists and is not a directory.")


def preflight_targets(targets: list[Path], force: bool) -> None:
    """Validate every target before any repo write begins."""

    seen: set[Path] = set()
    for target in targets:
        if target in seen:
            raise ValueError(f"Duplicate target path resolved for derived generation: {target}")
        seen.add(target)
        validate_target(target, force=force)


def ensure_target(target_dir: Path, force: bool, dry_run: bool) -> None:
    """Validate that the target directory is writable."""

    validate_target(target_dir, force=force)
    if target_dir.exists():
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


def _render_yaml_scalar(value: object) -> str:
    """Render one scalar safely into yaml."""

    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if re.fullmatch(r"[A-Za-z0-9_./:-]+", text):
        return text
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f"\"{escaped}\""


def _render_yaml_value(value: object, indent: int = 2) -> str:
    """Render a nested yaml-like structure using spaces only."""

    prefix = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                lines.append(f"{prefix}{key}:")
                lines.append(_render_yaml_value(child, indent + 2))
            else:
                lines.append(f"{prefix}{key}: {_render_yaml_scalar(child)}")
        return "\n".join(lines)
    if isinstance(value, list):
        if not value:
            return f"{prefix}[]"
        lines = []
        for item in value:
            if isinstance(item, (dict, list)):
                lines.append(f"{prefix}-")
                lines.append(_render_yaml_value(item, indent + 2))
            else:
                lines.append(f"{prefix}- {_render_yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{prefix}{_render_yaml_scalar(value)}"


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

This doc should describe implemented behavior, not planned architecture. If the repo is still mostly scaffolding, defer or keep this file extremely small.

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
    include_root_readme: bool,
    include_docs_dir: bool,
    docs_dir_generated: bool,
    compose_project_name_dev: str,
    compose_project_name_test: str,
    compose_files: list[str],
    port_map: dict[str, int],
    starter_paths: dict[str, str],
    validation_commands: list[str],
    vendored_manifest_paths: list[str],
    vendored_support_paths: list[str],
    prompt_directory: str,
    prompts_md_generated: bool,
    initial_prompt_files: list[str],
    extra_context_entrypoints: list[str] | None = None,
    extra_metadata: dict[str, object] | None = None,
) -> str:
    """Render the generated profile summary."""

    context_entrypoints = [
        "AGENT.md",
        "CLAUDE.md",
        "manifests/project-profile.yaml",
        ".generated-profile.yaml",
        *vendored_manifest_paths,
        *(["README.md"] if include_root_readme else []),
        *(["docs/repo-purpose.md", "docs/repo-layout.md"] if include_docs_dir else []),
    ]
    if extra_context_entrypoints:
        context_entrypoints.extend(extra_context_entrypoints)
    startup_order = list(dict.fromkeys(context_entrypoints))
    derived_metadata_lines = ""
    if extra_metadata:
        derived_metadata_lines = "derived_metadata:\n" + _render_yaml_value(extra_metadata, indent=2)
    values = {
        "repo_name": repo_name,
        "repo_slug": slug,
        "description": description,
        "archetype": archetype,
        "primary_stack": primary_stack,
        "front_docs_root_readme_generated": str(include_root_readme).lower(),
        "front_docs_docs_dir_generated": str(docs_dir_generated).lower(),
        "selected_manifest_lines": format_yaml_list(manifests),
        "vendored_manifest_lines": format_yaml_list(vendored_manifest_paths),
        "vendored_support_lines": format_yaml_list(vendored_support_paths),
        "startup_order_lines": format_yaml_list(startup_order),
        "prompt_directory": prompt_directory,
        "prompts_md_generated": str(prompts_md_generated).lower(),
        "initial_prompt_file_lines": format_yaml_list(initial_prompt_files),
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
        "context_entrypoint_lines": format_yaml_list(context_entrypoints),
        "front_docs_guidance_lines": format_yaml_list(
            [
                "delay root README.md until the repo has an implemented slice worth describing honestly",
                "delay a broad docs/ directory until several stable topics exist",
                "narrow operational docs are acceptable when explicitly needed",
            ]
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
        "derived_metadata_block": derived_metadata_lines,
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
        ".prompts/001-bootstrap-repo.txt": render_template(
            repo_root() / "templates/prompt-first/001-bootstrap.template.txt",
            values,
        ),
        ".prompts/002-refine-test-surface.txt": render_template(
            repo_root() / "templates/prompt-first/002-refine.template.txt",
            values,
        ),
    }


def _source_examples_for_derived(entry: dict[str, object]) -> list[tuple[int, ExampleProject]]:
    """Return source example metadata for one derived entry."""

    examples: list[tuple[int, ExampleProject]] = []
    for number in _coerce_int_list(entry.get("source_examples", [])):
        project = EXAMPLE_PROJECTS.get(number)
        if project is not None:
            examples.append((number, project))
    return examples


def _source_example_specs_for_derived(entry: dict[str, object]) -> list[dict[str, object]]:
    """Return repo-local source example metadata for one derived entry."""

    args_by_number: dict[int, dict[str, object]] = {}
    for item in entry.get("new_repo_args", []):
        if not isinstance(item, dict):
            continue
        args_by_number[int(item.get("example", 0))] = item

    specs: list[dict[str, object]] = []
    for number, project in _source_examples_for_derived(entry):
        item = args_by_number.get(number, {})
        specs.append(
            {
                "number": number,
                "codename": project.codename,
                "title": project.title,
                "archetype": str(item.get("archetype", project.archetype)),
                "primary_stack": str(item.get("primary_stack", project.primary_stack)),
                "smoke_tests": bool(item.get("smoke_tests", project.smoke_tests)),
                "integration_tests": bool(item.get("integration_tests", project.integration_tests)),
                "seed_data": bool(item.get("seed_data", project.seed_data)),
                "dokku": bool(item.get("dokku", project.dokku)),
            }
        )
    return specs


def _seam_contract_text(entry: dict[str, object]) -> str:
    """Extract the seam-contract sentence from a derived prompt when present."""

    prompt = str(entry.get("prompt", ""))
    match = re.search(r"The seam contracts are:\s*(.+?)(?:\.\s|$)", prompt, re.DOTALL)
    if not match:
        return "Document the seam contracts implied by the combined scenario."
    return " ".join(match.group(1).split())


def _derived_service_plan_lines(entry: dict[str, object]) -> list[str]:
    """Build service-by-service scaffold bullets from new_repo_args."""

    lines: list[str] = []
    for item in _source_example_specs_for_derived(entry):
        lines.append(
            f"- `{item['codename']}` from source example `#{item['number']}`: "
            f"{item['title']} ({item['archetype']} / {item['primary_stack']})"
        )
    return lines


def _derived_preferred_examples(selected_manifests: list[str], manifests: dict[str, dict[str, object]]) -> list[str]:
    """Collect preferred canonical example paths from selected manifests."""

    paths: list[str] = []
    for manifest_name in selected_manifests:
        manifest = manifests.get(manifest_name, {})
        preferred = manifest.get("preferred_examples", [])
        if isinstance(preferred, list):
            for path in preferred:
                path_text = str(path)
                if path_text not in paths:
                    paths.append(path_text)
    return paths


def render_derived_prompt_files(
    entry: dict[str, object],
    selected_manifests: list[str],
    manifests: dict[str, dict[str, object]],
    *,
    derived_context_mode: str,
    mode_bundle_paths: list[str],
    mode_bundle_records: list[dict[str, object]],
) -> dict[str, str]:
    """Render the derived prompt-first prompt sequence."""

    name = str(entry["name"])
    title = str(entry.get("title") or name)
    description = str(entry.get("description", ""))
    prompt_text = str(entry.get("prompt", "")).strip()
    vendored_manifest_paths = [f"manifests/base/{name}.yaml" for name in selected_manifests]
    manifest_startup_paths = _derived_manifest_startup_paths(selected_manifests, manifests)
    source_examples = _source_example_specs_for_derived(entry)
    source_lines = [
        f"- `#{item['number']}` `{item['codename']}`: {item['title']} "
        f"({item['archetype']} / {item['primary_stack']})"
        for item in source_examples
    ]
    source_detail_lines = [
        f"- Source example `#{item['number']}` keeps the lineage for `{item['codename']}`: "
        f"{item['title']}. Smoke tests: `{str(item['smoke_tests']).lower()}`; "
        f"integration tests: `{str(item['integration_tests']).lower()}`; "
        f"seed data: `{str(item['seed_data']).lower()}`; Dokku: `{str(item['dokku']).lower()}`."
        for item in source_examples
    ]
    scaffold_lines = _derived_service_plan_lines(entry)
    seam_contract_text = _seam_contract_text(entry)
    seam_notes = str(entry.get("seam_notes", "")).strip()
    preferred_examples = _derived_preferred_examples(selected_manifests, manifests)
    canonical_lines = [f"- `{path}`" for path in preferred_examples] or [
        "- `examples/derived/example-prompts.yaml`",
    ]
    maximal_bundle_lines = [
        f"- `{record['path']}` ({record['authority']}; {record['category']})"
        for record in mode_bundle_records
    ]
    maximal_startup_lines = [
        f"- `{path}`"
        for path in _derived_maximal_startup_paths(mode_bundle_records)
    ]
    bundle_mode_lines = [
        f"Derived context mode: `{derived_context_mode}`.",
        "Compact mode keeps the vendored bundle tightly scoped to the selected manifests."
        if derived_context_mode == "compact"
        else "Maximal mode intentionally vendors additional repo-local `context/`, `examples/`, and `templates/` material so prompt-first work can continue locally without assuming access to the source base repo.",
    ]
    prompt_01 = "\n".join(
        [
            f"# PROMPT_01: Bootstrap {name}",
            "",
            f"Scenario: `{title}`",
            f"Description: {description}",
            "This generated repo is a prompt-first descendant of `agent-context-base`.",
            "Treat the vendored base manifests and generated profiles in this repo as the local replacement for the source base repo's manifest-selection workflow.",
            "",
            "Start with these exact files in this order before coding:",
            "- `AGENT.md`",
            "- `CLAUDE.md`",
            "- `manifests/project-profile.yaml`",
            "- `.generated-profile.yaml`",
            *[f"- `{path}`" for path in vendored_manifest_paths],
            *[f"- `{path}`" for path in manifest_startup_paths],
            *maximal_startup_lines,
            "- `.prompts/PROMPT_01.txt`",
            "- `.prompts/PROMPT_02.txt`",
            "- `.prompts/PROMPT_03.txt`",
            "- `.prompts/PROMPT_04.txt`",
            "",
            *bundle_mode_lines,
            "",
            "Reconstruct the intended context bundle from those files before coding. Use the vendored manifests to recover required context, optional context, preferred examples, recommended templates, warnings, and bootstrap defaults.",
            *(
                [
                    "",
                    "Additional local routing and continuation materials vendored by maximal mode:",
                    *maximal_bundle_lines,
                    "",
                    "Read the startup subset first. Treat `context/` paths as authoritative guidance, `examples/` paths as informative canonical references, and `templates/` paths as templating references rather than generated state.",
                    "",
                    "Prefer those repo-local copies over assumptions about where the source base repo kept them.",
                ]
                if derived_context_mode == "maximal" and maximal_bundle_lines
                else []
            ),
            "",
            "Full derived scenario brief:",
            prompt_text,
            "",
            "Source examples driving this repo:",
            *source_lines,
            "",
            "Treat the source example metadata in `manifests/project-profile.yaml` as repo-local lineage records, not as commands that must be rerun from the parent repo.",
            "",
            "Instructions:",
            "- Treat this repo as the orchestration and implementation repo for the derived scenario, not as a blank shell and not as several unrelated repos.",
            "- Update `manifests/project-profile.yaml` and `.generated-profile.yaml` first so the startup order, vendored manifest paths, service map, seam map, and verification commands are explicit.",
            "- Prefer exact repo-path updates and concrete verification commands over vague planning notes.",
            "",
        ]
    )
    prompt_02 = "\n".join(
        [
            f"# PROMPT_02: Scaffold Service Surfaces For {name}",
            "",
            "Service-by-service scaffold plan:",
            *scaffold_lines,
            "",
            "Repo-local source example lineage to preserve while scaffolding:",
            *source_detail_lines,
            "",
            "Vendored manifest workflow:",
            *[f"- Load `{path}` and extract the required/optional context, preferred examples, recommended templates, warnings, and bootstrap defaults into repo-local planning." for path in vendored_manifest_paths],
            "",
            "Canonical references to pull shape from when available:",
            *canonical_lines,
            *(
                [
                    "",
                    "Maximal-mode local bundle available for routing, prompt generation, and continuation work:",
                    *maximal_bundle_lines,
                ]
                if derived_context_mode == "maximal" and maximal_bundle_lines
                else []
            ),
            "",
            "Instructions:",
            "- Name each service or subsystem explicitly in the combined service map.",
            "- Pull implementation shape from the vendored manifest metadata and the listed canonical examples instead of inventing new conventions.",
            "- Create scaffold placeholders only where they clarify ownership and seam boundaries.",
            "- Keep every file reference exact and repo-local.",
            "",
        ]
    )
    prompt_03 = "\n".join(
        [
            f"# PROMPT_03: Wire Seams And Contracts For {name}",
            "",
            "Keep the scenario-specific seam contracts grounded in the source examples and vendored manifest guidance.",
            "",
            "Seam contracts:",
            f"- {seam_contract_text}",
            *(["", "Seam notes:", seam_notes] if seam_notes else []),
            "",
            "Write or update seam docs under exact paths:",
            "- `docs/seams/README.md`",
            "- `docs/seams/event-contracts.md`",
            "- `docs/seams/rest-contracts.md`",
            "- `manifests/project-profile.yaml`",
            "- `.generated-profile.yaml`",
            *(
                [
                    "",
                    "Consult these additional repo-local routing and prompt-first files while wiring seams:",
                    *maximal_bundle_lines,
                ]
                if derived_context_mode == "maximal" and maximal_bundle_lines
                else []
            ),
            "",
            "Instructions:",
            "- Add schemas, event names, or REST seam docs under the exact paths above.",
            "- Keep service boundaries explicit, testable, and narrow.",
            "- Treat seam contracts as source-controlled interfaces, not prose-only suggestions.",
            "- If the initial four prompts are no longer sufficient, create the next prompt file under `.prompts/` using strictly monotonic numbering and exact path references.",
            "",
        ]
    )
    prompt_04 = "\n".join(
        [
            f"# PROMPT_04: Verify And Refine {name}",
            "",
            "Verification expectations:",
            "- Keep per-service smoke checks explicit for every source example included in this derived repo.",
            "- Add at least one combined integration or coordination check proving the main seam path for the scenario.",
            "- Record the exact verification command set in `manifests/project-profile.yaml`.",
            "- Use the repo-local source example metadata in `manifests/project-profile.yaml` to determine expected smoke, integration, seed-data, and deployment traits for each service.",
            *(
                [
                    "- Use the maximal-mode vendored local bundle for additional prompt-first doctrine, canonical examples, and workflow continuation material before inventing new repo conventions."
                ]
                if derived_context_mode == "maximal"
                else []
            ),
            "",
            "Instructions:",
            "- Add or update verification commands in `manifests/project-profile.yaml` for smoke checks and derived-specific integration checks.",
            "- Define the combined scenario's smoke and integration expectations before broadening implementation.",
            "- Continue creating or refining prompt files in `.prompts/` when more implementation batches are needed. Keep numbering strictly monotonic and reference exact repo paths in each new prompt.",
            "- Run a post-flight refinement pass and a doc freshness pass after the first meaningful slice lands.",
            "- Do not create speculative front docs or marketing-style root docs before the repo has an implemented slice worth describing.",
            "",
        ]
    )
    return {
        ".prompts/PROMPT_01.txt": prompt_01 + "\n",
        ".prompts/PROMPT_02.txt": prompt_02 + "\n",
        ".prompts/PROMPT_03.txt": prompt_03 + "\n",
        ".prompts/PROMPT_04.txt": prompt_04 + "\n",
    }


def _build_derived_profile_metadata(
    entry: dict[str, object],
    selected_manifests: list[str],
    manifests: dict[str, dict[str, object]],
    *,
    derived_context_mode: str,
    mode_bundle_paths: list[str],
    mode_bundle_records: list[dict[str, object]],
) -> dict[str, object]:
    """Build the derived-specific metadata block for the generated profile."""

    manifest_startup_paths = _derived_manifest_startup_paths(selected_manifests, manifests)
    maximal_startup_paths = _derived_maximal_startup_paths(mode_bundle_records)
    return {
        "derived_example_name": entry["name"],
        "derived_team": entry.get("team"),
        "derived_description": entry.get("description"),
        "derived_context_mode": derived_context_mode,
        "generated_repo_role": "orchestration-and-implementation",
        "descendant_of": "agent-context-base",
        "maximal_bundle_policy": {
            "name": DERIVED_MAXIMAL_BUNDLE_POLICY_NAME,
            "note": DERIVED_MAXIMAL_BUNDLE_POLICY_NOTE,
            "compact_bundle_source": "selected base manifests plus manifest-linked support assets",
            "maximal_bundle_source": "compact bundle plus explicit prompt-first continuation supplements",
        },
        "repo_local_substitute_for_base_repo": [
            "manifests/project-profile.yaml",
            ".generated-profile.yaml",
            *[f"manifests/base/{name}.yaml" for name in selected_manifests],
            *mode_bundle_paths,
        ],
        "repo_local_routing_model_paths": [
            "AGENT.md",
            "CLAUDE.md",
            "manifests/project-profile.yaml",
            ".generated-profile.yaml",
            *[f"manifests/base/{name}.yaml" for name in selected_manifests],
            *mode_bundle_paths,
        ],
        "source_examples": [
            {
                "number": item["number"],
                "codename": item["codename"],
                "title": item["title"],
                "archetype": item["archetype"],
                "primary_stack": item["primary_stack"],
                "smoke_tests": item["smoke_tests"],
                "integration_tests": item["integration_tests"],
                "seed_data": item["seed_data"],
                "dokku": item["dokku"],
            }
            for item in _source_example_specs_for_derived(entry)
        ],
        "source_example_lineage_note": (
            "Source example numbers and codenames are preserved here as repo-local lineage "
            "metadata. They are descriptive startup inputs for this generated repo, not "
            "commands that require rerunning agent-context-base generation."
        ),
        "preferred_examples": _derived_preferred_examples(selected_manifests, manifests),
        "local_canonical_examples_available": [
            path
            for path in (
                _derived_preferred_examples(selected_manifests, manifests)
                + [item for item in mode_bundle_paths if item.startswith("examples/")]
            )
        ],
        "local_canonical_workflows_available": [
            path for path in mode_bundle_paths if path.startswith("examples/canonical-workflows/")
        ],
        "selected_manifests": selected_manifests,
        "vendored_manifest_paths": [f"manifests/base/{name}.yaml" for name in selected_manifests],
        "manifest_bundle_startup_paths": manifest_startup_paths,
        "mode_vendored_paths": mode_bundle_paths,
        "maximal_bundle_paths": mode_bundle_paths,
        "maximal_bundle_startup_paths": maximal_startup_paths,
        "maximal_bundle_records": mode_bundle_records,
        "downstream_startup_order": [
            "AGENT.md",
            "CLAUDE.md",
            "manifests/project-profile.yaml",
            ".generated-profile.yaml",
            *[f"manifests/base/{name}.yaml" for name in selected_manifests],
            *manifest_startup_paths,
            *maximal_startup_paths,
            ".prompts/PROMPT_01.txt",
            ".prompts/PROMPT_02.txt",
            ".prompts/PROMPT_03.txt",
            ".prompts/PROMPT_04.txt",
            *[path for path in mode_bundle_paths if path not in maximal_startup_paths],
        ],
        "prompt_directory": ".prompts",
        "prompts_md_absent_by_design": True,
        "prompt_sequence": [
            "PROMPT_01.txt",
            "PROMPT_02.txt",
            "PROMPT_03.txt",
            "PROMPT_04.txt",
        ],
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
        "scripts/check_repo.py": """#!/usr/bin/env python3\n\"\"\"Check the minimal prompt-first repo surface exists.\"\"\"\n\nfrom pathlib import Path\n\n\ndef main() -> None:\n    required = [Path(\"AGENT.md\"), Path(\"CLAUDE.md\"), Path(\".prompts\")]\n    missing = [path.as_posix() for path in required if not path.exists()]\n    if missing:\n        raise SystemExit(f\"Missing required files: {missing}\")\n    print(\"repo surface looks present\")\n\n\nif __name__ == \"__main__\":\n    main()\n""",
        "scripts/check_generated_profile.py": """#!/usr/bin/env python3\n\"\"\"Check the generated profile file exists.\"\"\"\n\nfrom pathlib import Path\n\n\ndef main() -> None:\n    profile = Path(\".generated-profile.yaml\")\n    if not profile.exists():\n        raise SystemExit(\".generated-profile.yaml is missing\")\n    print(\"generated profile exists\")\n\n\nif __name__ == \"__main__\":\n    main()\n""",
        "scripts/validate_repo.py": """#!/usr/bin/env python3\n\"\"\"Validate the prompt-first starter repo surface.\"\"\"\n\nimport re\nfrom pathlib import Path\n\n\nCLASSIC_PROMPTS = [\"001-bootstrap-repo.txt\", \"002-refine-test-surface.txt\"]\nDERIVED_PROMPT_PATTERN = re.compile(r\"^PROMPT_(\\d{2})\\.txt$\")\n\n\ndef _validate_prompt_files(prompt_files: list[str]) -> None:\n    if not prompt_files:\n        raise SystemExit(\".prompts must contain at least one prompt file\")\n    if prompt_files == CLASSIC_PROMPTS:\n        return\n    derived_numbers: list[int] = []\n    for filename in prompt_files:\n        match = DERIVED_PROMPT_PATTERN.fullmatch(filename)\n        if match is None:\n            raise SystemExit(\n                \"Prompt files must be either the classic 001/002 pair or a pure PROMPT_XX.txt sequence: \"\n                f\"{prompt_files}\"\n            )\n        derived_numbers.append(int(match.group(1)))\n    expected_numbers = list(range(1, len(derived_numbers) + 1))\n    if derived_numbers != expected_numbers:\n        raise SystemExit(f\"Derived prompt files must stay monotonic: {prompt_files}\")\n\n\ndef main() -> None:\n    required = [\n        Path(\"AGENT.md\"),\n        Path(\"CLAUDE.md\"),\n        Path(\"manifests/project-profile.yaml\"),\n    ]\n    missing = [path.as_posix() for path in required if not path.exists()]\n    if missing:\n        raise SystemExit(f\"Missing required files: {missing}\")\n\n    prompt_dir = Path(\".prompts\")\n    if not prompt_dir.exists() or not prompt_dir.is_dir():\n        raise SystemExit(\".prompts directory is missing\")\n    prompt_files = sorted(path.name for path in prompt_dir.glob(\"*.txt\"))\n    _validate_prompt_files(prompt_files)\n\n    print(\"repo validation passed\")\n\n\nif __name__ == \"__main__\":\n    main()\n""",
        "scripts/seed_data.py": """#!/usr/bin/env python3\n\"\"\"Write deterministic prompt-first starter notes.\"\"\"\n\nfrom pathlib import Path\n\n\ndef main() -> None:\n    target = Path(\"artifacts/generated-notes.txt\")\n    target.parent.mkdir(parents=True, exist_ok=True)\n    target.write_text(\"replace with deterministic repo notes\\n\", encoding=\"utf-8\")\n    print(f\"Wrote {target}\")\n\n\nif __name__ == \"__main__\":\n    main()\n""",
    }


def render_derived_seam_placeholder_files(repo_name: str) -> dict[str, str]:
    """Render initial seam docs for derived prompt-first repos."""

    return {
        "docs/seams/README.md": (
            "# Seam Docs\n\n"
            f"Use this directory to record the owned seams for `{repo_name}`.\n"
            "Keep event and REST contracts explicit, versioned, and repo-local.\n"
        ),
        "docs/seams/event-contracts.md": (
            "# Event Contracts\n\n"
            "Record event names, producers, consumers, and payload fields here.\n"
        ),
        "docs/seams/rest-contracts.md": (
            "# REST Contracts\n\n"
            "Record request and response shapes for cross-service HTTP seams here.\n"
        ),
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


def render_zig_starters() -> dict[str, str]:
    """Render Zig starter app and tests."""

    return {
        "src/main.zig": """const std = @import(\"std\");\n\npub fn main() !void {\n    std.debug.print(\"replace with Zap listener or Jetzig app wiring\\n\", .{});\n}\n""",
        "tests/smoke/health_test.zig": """const std = @import(\"std\");\n\ntest \"health smoke placeholder\" {\n    try std.testing.expect(true);\n}\n""",
        "tests/integration/report_runs_test.zig": """const std = @import(\"std\");\n\ntest \"report runs integration placeholder\" {\n    try std.testing.expect(true);\n}\n""",
        "scripts/seed_data.zig": """const std = @import(\"std\");\n\npub fn main() !void {\n    std.debug.print(\"replace with deterministic Zig seed generation\\n\", .{});\n}\n""",
    }


def render_kotlin_starters() -> dict[str, str]:
    """Render Kotlin starter app and tests."""

    return {
        "build.gradle.kts": """plugins {\n    kotlin(\"jvm\") version \"1.9.24\"\n    application\n}\n\nrepositories {\n    mavenCentral()\n}\n\ndependencies {\n    implementation(\"org.http4k:http4k-core:5.33.0.0\")\n    implementation(\"org.http4k:http4k-server-jetty:5.33.0.0\")\n    implementation(\"org.jetbrains.exposed:exposed-core:0.50.1\")\n    implementation(\"org.jetbrains.exposed:exposed-jdbc:0.50.1\")\n    implementation(\"com.h2database:h2:2.2.224\")\n    implementation(\"ch.qos.logback:logback-classic:1.5.6\")\n    testImplementation(kotlin(\"test\"))\n}\n\napplication {\n    mainClass.set(\"app.MainKt\")\n}\n\nkotlin {\n    jvmToolchain(21)\n}\n""",
        "settings.gradle.kts": "rootProject.name = \"app\"\n",
        "src/main/kotlin/app/Main.kt": """package app\n\nimport org.http4k.core.Method.GET\nimport org.http4k.core.Response\nimport org.http4k.core.Status\nimport org.http4k.routing.bind\nimport org.http4k.routing.routes\nimport org.http4k.server.Jetty\nimport org.http4k.server.asServer\n\nfun main() {\n    val app = routes(\n        \"/healthz\" bind GET to { Response(Status.OK).body(\"{\\\"status\\\":\\\"ok\\\"}\").header(\"content-type\", \"application/json\") },\n    )\n    app.asServer(Jetty(8080)).start()\n    Thread.currentThread().join()\n}\n""",
        "src/test/kotlin/app/HealthSmokeTest.kt": """package app\n\nimport kotlin.test.Test\nimport kotlin.test.assertTrue\n\nclass HealthSmokeTest {\n    @Test\n    fun placeholder() {\n        assertTrue(true)\n    }\n}\n""",
        "src/test/kotlin/app/ReportRunsIntegrationTest.kt": """package app\n\nimport kotlin.test.Test\nimport kotlin.test.assertTrue\n\nclass ReportRunsIntegrationTest {\n    @Test\n    fun placeholder() {\n        assertTrue(true)\n    }\n}\n""",
        "scripts/seed_data.sql": "insert into reports (tenant_id, report_id, total_events, status) values ('acme', 'daily-signups', 42, 'ready');\n",
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


def render_nim_starters() -> dict[str, str]:
    """Render Nim starter app and tests."""

    return {
        "src/main.nim": 'import jester\n\nroutes:\n  get "/healthz":\n    resp %*{"status": "ok"}\n\nwhen isMainModule:\n  let settings = newSettings(port=Port(5000))\n  var jester = initJester(router, settings=settings)\n  jester.serve()\n',
        "tests/smoke/health_smoke.nim": 'import unittest\n\nsuite "health smoke":\n  test "placeholder":\n    check true\n',
        "tests/integration/report_runs_integration.nim": 'import unittest\n\nsuite "report runs integration":\n  test "placeholder":\n    # Replace with docker-compose.test.yml boot plus one real round-trip assertion.\n    check true\n',
        "scripts/seed_data.nim": 'proc main() =\n  echo "replace with deterministic seed data"\n\nwhen isMainModule:\n  main()\n',
    }


def render_scala_starters() -> dict[str, str]:
    """Render Scala starter app and tests."""

    return {
        "src/main/scala/app/Main.scala": 'package app\n\nobject Main extends App {\n  println("replace with Tapir + http4s + ZIO server wiring")\n}\n',
        "src/test/scala/app/HealthSmokeTest.scala": 'package app\n\nimport org.scalatest.flatspec.AnyFlatSpec\nimport org.scalatest.matchers.should.Matchers\n\nclass HealthSmokeTest extends AnyFlatSpec with Matchers {\n  "health" should "be a placeholder" in {\n    true shouldBe true\n  }\n}\n',
        "src/test/scala/app/ReportRunsIntegrationTest.scala": 'package app\n\nimport org.scalatest.flatspec.AnyFlatSpec\nimport org.scalatest.matchers.should.Matchers\n\nclass ReportRunsIntegrationTest extends AnyFlatSpec with Matchers {\n  "report runs" should "placeholder" in {\n    // Replace with docker-compose.test.yml boot plus one real boundary assertion.\n    true shouldBe true\n  }\n}\n',
        "scripts/seed_data.sql": "insert into report_runs (tenant_id, report_id, total_events) values ('acme', 'daily-signups', 42);\n",
    }


def render_clojure_starters() -> dict[str, str]:
    """Render Clojure starter app and tests."""

    return {
        "src/app/routes.clj": '(ns app.routes\n  (:require [ring.util.response :as response]))\n\n(defn healthz-handler [_request]\n  (response/response {:status "ok"}))\n\n(def routes\n  [[\"/healthz\" {:get {:handler healthz-handler}}]])\n',
        "test/app/health_smoke_test.clj": "(ns app.health-smoke-test\n  (:require [clojure.test :refer [deftest is]]))\n\n(deftest health-smoke-placeholder\n  (is true))\n",
        "test/app/report_runs_integration_test.clj": "(ns app.report-runs-integration-test\n  (:require [clojure.test :refer [deftest is]]))\n\n(deftest report-runs-integration-placeholder\n  ;; Replace with docker-compose.test.yml boot plus one real next.jdbc query.\n  (is true))\n",
        "scripts/seed_data.sql": "insert into report_runs (tenant_id, report_id, total_events) values ('acme', 'daily-signups', 42);\n",
    }


def render_dart_starters() -> dict[str, str]:
    """Render Dart Frog starter app and tests."""

    return {
        "routes/index.dart": "import 'package:dart_frog/dart_frog.dart';\n\nResponse onRequest(RequestContext context) {\n  return Response.json(body: {'status': 'ok'});\n}\n",
        "test/health_smoke_test.dart": "import 'package:test/test.dart';\n\nvoid main() {\n  test('health smoke placeholder', () {\n    expect(true, isTrue);\n  });\n}\n",
        "test/report_runs_integration_test.dart": "import 'package:test/test.dart';\n\nvoid main() {\n  test('report runs integration placeholder', () {\n    // Replace with docker-compose.test.yml boot plus one real round-trip assertion.\n    expect(true, isTrue);\n  });\n}\n",
        "scripts/seed_data.dart": "void main() {\n  print('replace with deterministic seed data');\n}\n",
    }


def render_crystal_starters() -> dict[str, str]:
    """Render Crystal + Kemal + Avram starter app and tests."""

    return {
        "src/routes/reports.cr": 'require "kemal"\n\nget "/reports/summary" do |env|\n  env.response.content_type = "application/json"\n  {report_id: "daily-signups", status: "ready"}.to_json\nend\n',
        "spec/smoke/health_spec.cr": 'require "spec"\n\ndescribe "health smoke" do\n  it "placeholder" do\n    true.should be_true\n  end\nend\n',
        "spec/integration/report_runs_spec.cr": 'require "spec"\n\ndescribe "report runs integration" do\n  it "placeholder" do\n    # Replace with docker-compose.test.yml boot and a real round-trip assertion.\n    true.should be_true\n  end\nend\n',
        "scripts/seed_data.cr": '# Replace with deterministic seed data.\nputs "seed data placeholder"\n',
    }


def render_ruby_starters() -> dict[str, str]:
    """Render Ruby + Hanami starter actions and tests."""

    return {
        "app/actions/reports/index.rb": 'module Actions\n  module Reports\n    class Index < Hanami::Action\n      def handle(request, response)\n        response.body = [{report_id: "daily-signups", status: "ready"}].to_json\n      end\n    end\n  end\nend\n',
        "spec/smoke/health_spec.rb": "require 'spec_helper'\n\nRSpec.describe 'health smoke' do\n  it 'placeholder' do\n    expect(true).to be true\n  end\nend\n",
        "spec/integration/report_runs_spec.rb": "require 'spec_helper'\n\nRSpec.describe 'report runs integration' do\n  it 'placeholder' do\n    # Replace with docker-compose.test.yml boot and a real round-trip assertion.\n    expect(true).to be true\n  end\nend\n",
        "scripts/seed_data.rb": "# Replace with deterministic seed data.\nputs 'seed data placeholder'\n",
    }


def render_ocaml_starters() -> dict[str, str]:
    """Render OCaml + Dream + Caqti + Tyxml starter app and tests."""

    return {
        "bin/routes.ml": 'let routes =\n  [\n    Dream.get "/reports/summary" (fun _ ->\n      Dream.json {|{"report_id":"daily-signups","status":"ready"}|});\n  ]\n',
        "test/smoke/test_health.ml": 'let () =\n  (* health smoke placeholder *)\n  assert true\n',
        "test/integration/test_report_runs.ml": '(* Replace with docker-compose.test.yml boot and a real round-trip assertion. *)\nlet () = assert true\n',
        "scripts/seed_data.ml": '(* Replace with deterministic seed data. *)\nlet () = print_endline "seed data placeholder"\n',
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
    if primary_stack == "kotlin-http4k-exposed":
        return render_kotlin_starters()
    if primary_stack == "zig-zap-jetzig":
        return render_zig_starters()
    if primary_stack == "go-echo":
        return render_go_starters()
    if primary_stack == "elixir-phoenix":
        return render_phoenix_starters(slug)
    if primary_stack == "nim-jester-happyx":
        return render_nim_starters()
    if primary_stack == "scala-tapir-http4s-zio":
        return render_scala_starters()
    if primary_stack == "clojure-kit-nextjdbc-hiccup":
        return render_clojure_starters()
    if primary_stack == "dart-dartfrog":
        return render_dart_starters()
    if primary_stack == "crystal-kemal-avram":
        return render_crystal_starters()
    if primary_stack == "ruby-hanami":
        return render_ruby_starters()
    if primary_stack == "ocaml-dream-caqti-tyxml":
        return render_ocaml_starters()
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
            "route": ".prompts/001-bootstrap-repo.txt",
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


def build_generated_files(
    request: RepoGenerationRequest,
    manifests: dict[str, dict[str, object]],
) -> dict[str, str]:
    """Build the full generated file set for one repo request."""

    if request.primary_stack not in STACKS:
        raise ValueError(f"Unsupported stack: {request.primary_stack}")
    if request.archetype not in ARCHETYPES:
        raise ValueError(f"Unsupported archetype: {request.archetype}")
    for manifest_name in request.manifests:
        if manifest_name not in manifests:
            raise ValueError(f"Unknown manifest: {manifest_name}")

    slug = slugify(request.repo_name)
    profile = STACKS[request.primary_stack]
    description = request.description or f"Starter repo for {request.repo_name} using {profile.display_name}."
    docs_dir_generated = request.include_docs_dir or request.dokku
    docker_enabled = request.docker_layout or bool(
        infer_support_services(request.archetype, request.primary_stack, request.manifests)
    )

    selected_manifest_data = [manifests[name] for name in request.manifests]
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

    compose_project_name_dev = str(primary_manifest["compose_project_name_dev"]).replace("{repo_slug}", slug)
    compose_project_name_test = str(primary_manifest["compose_project_name_test"]).replace("{repo_slug}", slug)
    app_port = pick_port(str(primary_manifest["port_band_app_dev"]), slug)
    test_app_port = pick_port(str(primary_manifest["port_band_app_test"]), slug)
    support_services = infer_support_services(request.archetype, request.primary_stack, request.manifests)
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
    validate_bootstrap_plan(
        compose_project_name_dev=compose_project_name_dev,
        compose_project_name_test=compose_project_name_test,
        app_port=app_port,
        test_app_port=test_app_port,
        dev_support_ports={f"{name}_dev": port for name, port in dev_support_ports.items()},
        test_support_ports={f"{name}_test": port for name, port in test_support_ports.items()},
    )

    generated_files: dict[str, str] = {}
    generated_files.update(render_agent_and_claude(request.archetype, request.primary_stack, request.manifests))
    generated_files[".gitignore"] = render_gitignore(profile)
    vendored_manifest_texts = load_manifest_texts(request.manifests)
    vendored_support_texts = load_manifest_support_asset_texts(request.manifests, manifests)
    extra_vendored_paths = _dedupe_existing_repo_paths(request.extra_vendored_paths or [])
    for relative_path in extra_vendored_paths:
        vendored_support_texts.setdefault(
            relative_path,
            (repo_root() / relative_path).read_text(encoding="utf-8"),
        )
    vendored_manifest_paths = [
        f"manifests/base/{manifest_name}.yaml"
        for manifest_name in request.manifests
    ]
    for manifest_name, manifest_text in vendored_manifest_texts.items():
        generated_files[f"manifests/base/{manifest_name}.yaml"] = manifest_text
    for relative_path, asset_text in vendored_support_texts.items():
        generated_files[relative_path] = asset_text
    if request.include_root_readme:
        generated_files["README.md"] = render_readme(
            request.repo_name,
            description,
            request.archetype,
            profile,
            request.manifests,
            request.dokku,
            request.prompt_first,
            docker_enabled,
            app_port,
            compose_project_name_dev,
            compose_project_name_test,
            dev_support_ports,
            test_support_ports,
        )
    if request.include_docs_dir:
        generated_files.update(build_docs(request.repo_name, description, request.archetype, profile, request.manifests))

    starter_paths = resolved_starter_paths(request.primary_stack, slug)
    prompt_files = sorted(
        path
        for path in (request.prompt_files_override or {}).keys()
        if path.startswith(".prompts/")
    )
    if request.prompt_first and not prompt_files:
        prompt_files = sorted(render_prompt_files(request.repo_name, profile).keys())
    if request.primary_stack == "prompt-first-repo" and prompt_files:
        starter_paths["route"] = prompt_files[0]
    port_map = {"app_dev": app_port, "app_test": test_app_port}
    port_map.update({f"{name}_dev": port for name, port in dev_support_ports.items()})
    port_map.update({f"{name}_test": port for name, port in test_support_ports.items()})
    validation_commands = ["python scripts/validate_repo.py"] if request.primary_stack == "prompt-first-repo" else []
    if docker_enabled:
        validation_commands.append("docker compose -f docker-compose.test.yml config")
    profile_summary = render_profile_summary(
        repo_name=request.repo_name,
        slug=slug,
        description=description,
        archetype=request.archetype,
        primary_stack=request.primary_stack,
        manifests=request.manifests,
        docker_enabled=docker_enabled,
        dokku=request.dokku,
        prompt_first=request.prompt_first,
        smoke_tests=request.smoke_tests,
        integration_tests=request.integration_tests,
        seed_data=request.seed_data,
        include_root_readme=request.include_root_readme,
        include_docs_dir=request.include_docs_dir,
        docs_dir_generated=docs_dir_generated,
        compose_project_name_dev=compose_project_name_dev,
        compose_project_name_test=compose_project_name_test,
        compose_files=["docker-compose.yml", "docker-compose.test.yml"],
        port_map=port_map,
        starter_paths=starter_paths,
        validation_commands=validation_commands or ["echo no extra validation commands configured"],
        vendored_manifest_paths=vendored_manifest_paths,
        vendored_support_paths=sorted(vendored_support_texts),
        prompt_directory=".prompts" if request.prompt_first else "none",
        prompts_md_generated=False,
        initial_prompt_files=prompt_files if request.prompt_first else ["none"],
        extra_context_entrypoints=request.extra_context_entrypoints,
        extra_metadata=request.extra_profile_metadata,
    )
    generated_files["manifests/project-profile.yaml"] = profile_summary
    if not request.no_profile:
        generated_files[".generated-profile.yaml"] = profile_summary

    starter_files = starter_files_for_stack(request.primary_stack, slug)
    route_only_keys = set()
    if request.primary_stack == "python-fastapi-uv-ruff-orjson-polars":
        route_only_keys.update({"app/main.py", profile.route_path, "app/__init__.py", "app/api/__init__.py"})
    elif request.primary_stack == "typescript-hono-bun":
        route_only_keys.update({"src/index.ts", profile.route_path})
    elif request.primary_stack == "rust-axum-modern":
        route_only_keys.update({"src/main.rs"})
    elif request.primary_stack == "kotlin-http4k-exposed":
        route_only_keys.update({"build.gradle.kts", "settings.gradle.kts", "src/main/kotlin/app/Main.kt"})
    elif request.primary_stack == "zig-zap-jetzig":
        route_only_keys.update({"src/main.zig"})
    elif request.primary_stack == "go-echo":
        route_only_keys.update({"cmd/server/main.go"})
    elif request.primary_stack == "elixir-phoenix":
        route_only_keys.update({starter_paths["route"], f"lib/{phoenix_app_name(slug)}_web/controllers/health_controller.ex"})
    elif request.primary_stack == "prompt-first-repo":
        route_only_keys.update({"scripts/validate_repo.py"})
    elif request.primary_stack in {"crystal-kemal-avram", "ruby-hanami", "ocaml-dream-caqti-tyxml"}:
        route_only_keys.update({starter_paths["route"]})
    else:
        route_only_keys.update({starter_paths["route"], "app/__init__.py"})
    for relative_path, content in starter_files.items():
        should_write = relative_path in route_only_keys
        if request.smoke_tests and relative_path == starter_paths["smoke"]:
            should_write = True
        if request.integration_tests and relative_path == starter_paths["integration"]:
            should_write = True
        if request.seed_data and relative_path == starter_paths["seed"]:
            should_write = True
        if should_write:
            generated_files[relative_path] = content

    if request.derived_context_mode is not None:
        generated_files.update(render_derived_seam_placeholder_files(request.repo_name))

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

    if profile.extra_template and request.include_docs_dir:
        generated_files["docs/stack-notes.md"] = render_template(
            repo_root() / profile.extra_template,
            {},
        )

    if request.prompt_first:
        prompt_file_map = request.prompt_files_override or render_prompt_files(request.repo_name, profile)
        generated_files.update(prompt_file_map)
    if request.dokku:
        generated_files.update(render_dokku_files(slug, app_port))

    for directory in profile.directories:
        if directory == "docs" and not docs_dir_generated:
            continue
        generated_files.setdefault(f"{directory}/.gitkeep", "")

    return generated_files


def generate_repo(request: RepoGenerationRequest, manifests: dict[str, dict[str, object]]) -> dict[str, str]:
    """Generate one repo, printing either the dry-run plan or the final success message."""

    ensure_target(request.target_dir, force=request.force, dry_run=request.dry_run)
    generated_files = build_generated_files(request, manifests)
    if request.dry_run:
        print(f"Target: {request.target_dir}")
        print("Planned files:")
        write_files(request.target_dir, generated_files, dry_run=True)
        return generated_files
    write_files(request.target_dir, generated_files, dry_run=False)
    print(f"Generated starter repo at {request.target_dir}")
    return generated_files


def _build_derived_request(
    entry: dict[str, object],
    target_dir: Path,
    manifests: dict[str, dict[str, object]],
    *,
    derived_context_mode: str,
    force: bool,
    dry_run: bool,
) -> RepoGenerationRequest:
    """Build the prompt-first repo request for one derived leaf entry."""

    selected_manifests = ["prompt-first-meta-repo"]
    mode_bundle_paths = (
        _derived_maximal_bundle_paths(entry, selected_manifests, manifests)
        if derived_context_mode == "maximal"
        else []
    )
    mode_bundle_records = (
        _derived_maximal_bundle_records(entry, selected_manifests, manifests)
        if derived_context_mode == "maximal"
        else []
    )
    manifest_startup_paths = _derived_manifest_startup_paths(selected_manifests, manifests)
    startup_mode_paths = _derived_maximal_startup_paths(mode_bundle_records)
    return RepoGenerationRequest(
        repo_name=str(entry["name"]),
        target_dir=target_dir,
        archetype="prompt-first-repo",
        primary_stack="prompt-first-repo",
        manifests=selected_manifests,
        dokku=False,
        prompt_first=True,
        smoke_tests=True,
        integration_tests=True,
        seed_data=True,
        docker_layout=False,
        include_root_readme=False,
        include_docs_dir=False,
        no_profile=False,
        force=force,
        dry_run=dry_run,
        derived_context_mode=derived_context_mode,
        extra_vendored_paths=mode_bundle_paths,
        description=f"Derived orchestration repo for {entry['name']}: {entry.get('description', '')}",
        prompt_files_override=render_derived_prompt_files(
            entry,
            selected_manifests,
            manifests,
            derived_context_mode=derived_context_mode,
            mode_bundle_paths=mode_bundle_paths,
            mode_bundle_records=mode_bundle_records,
        ),
        extra_profile_metadata=_build_derived_profile_metadata(
            entry,
            selected_manifests,
            manifests,
            derived_context_mode=derived_context_mode,
            mode_bundle_paths=mode_bundle_paths,
            mode_bundle_records=mode_bundle_records,
        ),
        extra_context_entrypoints=[
            *manifest_startup_paths,
            *startup_mode_paths,
            ".prompts/PROMPT_01.txt",
            ".prompts/PROMPT_02.txt",
            ".prompts/PROMPT_03.txt",
            ".prompts/PROMPT_04.txt",
            *[path for path in mode_bundle_paths if path not in startup_mode_paths],
        ],
    )


def _print_derived_entry_summary(entry: dict[str, object], target_dir: Path) -> None:
    """Print the derived scenario details before generation or dry-run output."""

    print(f"=== {entry['name']} ===")
    print(f"Team: {entry.get('team', '?')} — {entry.get('team_name', '')}")
    print(f"Target: {target_dir}")
    print(f"Description: {entry.get('description', '')}")
    print()
    print("--- Prompt ---")
    print(str(entry.get("prompt", "")).strip())
    print()


def handle_derived_example(
    args: argparse.Namespace,
    manifests: dict[str, dict[str, object]],
) -> int:
    """Handle derived leaf generation, derived collections, and spin-out display."""

    selector = args.derived_example
    data = _load_derived_data()
    spin_out = next((entry for entry in data["spin_outs"] if entry.get("name") == selector), None)
    if spin_out is not None:
        print(f"=== {spin_out['name']} ===")
        print(f"Spin-out Platform: {spin_out.get('title', spin_out['name'])}")
        print(f"Origin: {spin_out.get('origin', '?')}")
        print(f"\nDescription: {spin_out['description']}")
        print("\n--- What It Becomes ---")
        print(str(spin_out.get("what_it_becomes", "")).strip())
        if spin_out.get("seam_notes"):
            print("\n--- Seam Notes ---")
            print(str(spin_out.get("seam_notes", "")).strip())
        return 0

    entries = _expand_derived_selector(selector, data)
    if not entries:
        print(f"Unknown derived example: {selector!r}. Use --list-derived to see available names.")
        return 1

    target_plans = _resolve_derived_targets(selector, entries, args.target_dir)
    preflight_targets([plan.target_dir for plan in target_plans], force=args.force)
    for index, plan in enumerate(target_plans):
        if index:
            print()
        _print_derived_entry_summary(plan.entry, plan.target_dir)
        request = _build_derived_request(
            plan.entry,
            plan.target_dir,
            manifests,
            derived_context_mode=args.derived_context_mode,
            force=args.force,
            dry_run=args.dry_run,
        )
        generate_repo(request, manifests)
    return 0


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

    if args.list_derived:
        data = _load_derived_data()
        if not data["derived"] and not data["spin_outs"]:
            print("No derived examples found. Run PROMPT_76 and PROMPT_78 to generate them.")
            return 0
        if data["derived"]:
            print("Derived Examples (sub-groups):")
            for entry in data["derived"]:
                print(f"  {entry['name']:<40}  Team {entry['team']}  {entry['description']}")
        if data["spin_outs"]:
            print()
            print("Spin-out Platforms:")
            for entry in data["spin_outs"]:
                print(f"  {entry['name']:<40}  {entry['origin']:<12}  {entry['description']}")
        print()
        print("Collection Selectors:")
        for selector in DERIVED_COLLECTION_SELECTORS:
            print(f"  {selector}")
        return 0

    if args.derived_example is not None:
        return handle_derived_example(args, manifests)

    if args.derived_context_mode != "compact":
        parser.error("--derived-context-mode only applies with --derived-example")

    if args.list_examples:
        for category_name, num_range in EXAMPLE_CATEGORIES:
            print(f"\n{category_name}")
            for n in num_range:
                if n in EXAMPLE_PROJECTS:
                    ex = EXAMPLE_PROJECTS[n]
                    print(f"  {n:>3}  {ex.codename}")
        return 0

    if args.use_example is not None:
        n = args.use_example
        if n not in EXAMPLE_PROJECTS:
            print(f"Unknown example number: {n}. Use --list-examples to see available projects.", file=sys.stderr)
            return 1
        entry = EXAMPLE_PROJECTS[n]
        if not args.archetype:
            args.archetype = entry.archetype
        if not args.primary_stack:
            args.primary_stack = entry.primary_stack
        if not args.dokku:
            args.dokku = entry.dokku
        if not args.smoke_tests:
            args.smoke_tests = entry.smoke_tests
        if not args.integration_tests:
            args.integration_tests = entry.integration_tests
        if not args.seed_data:
            args.seed_data = entry.seed_data
        if not args.repo_name:
            args.repo_name = f"{n:03d}-{entry.codename}"

    if not args.repo_name:
        parser.error("repo_name is required unless a --list-* flag is used")
    if not args.archetype:
        parser.error("--archetype is required")
    if not args.primary_stack:
        parser.error("--primary-stack is required")

    repo_name = args.repo_name
    target_dir = _normalize_resolved_path(Path(args.target_dir or slugify(repo_name)))
    selected_manifests = sorted(
        set(
            args.manifest
            or default_manifests_for(args.archetype, args.primary_stack, args.dokku)
        )
    )
    request = RepoGenerationRequest(
        repo_name=repo_name,
        target_dir=target_dir,
        archetype=args.archetype,
        primary_stack=args.primary_stack,
        manifests=selected_manifests,
        dokku=args.dokku,
        prompt_first=args.prompt_first or args.archetype == "prompt-first-repo",
        smoke_tests=args.smoke_tests,
        integration_tests=args.integration_tests,
        seed_data=args.seed_data,
        docker_layout=args.docker_layout,
        include_root_readme=args.include_root_readme,
        include_docs_dir=args.include_docs_dir,
        no_profile=args.no_profile,
        force=args.force,
        dry_run=args.dry_run,
    )
    generate_repo(request, manifests)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
