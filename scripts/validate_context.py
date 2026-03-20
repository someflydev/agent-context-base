#!/usr/bin/env python3
"""Validate repository context health, metadata integrity, and bootstrap invariants."""

from __future__ import annotations

import re
import sys
import tempfile
from contextlib import redirect_stdout
from os import devnull
from pathlib import Path

import new_repo
from context_tools import (
    validate_context_weights,
    validate_data_acquisition_consistency,
    validate_example_catalog,
    validate_markdown_cross_references,
    validate_mermaid_reference_hints,
    validate_prompt_numbering,
    validate_repo_signal_hints,
)
from manifest_tools import validate_manifest


BOOTSTRAP_CASES = (
    {"archetype": "backend-api-service", "primary_stack": "python-fastapi-uv-ruff-orjson-polars", "dokku": False},
    {
        "archetype": "backend-api-service",
        "primary_stack": "python-fastapi-uv-ruff-orjson-polars",
        "dokku": False,
        "include_root_readme": True,
        "include_docs_dir": True,
    },
    {"archetype": "backend-api-service", "primary_stack": "typescript-hono-bun", "dokku": False},
    {"archetype": "backend-api-service", "primary_stack": "rust-axum-modern", "dokku": False},
    {"archetype": "backend-api-service", "primary_stack": "zig-zap-jetzig", "dokku": False},
    {"archetype": "backend-api-service", "primary_stack": "go-echo", "dokku": False},
    {"archetype": "backend-api-service", "primary_stack": "kotlin-http4k-exposed", "dokku": False},
    {"archetype": "backend-api-service", "primary_stack": "elixir-phoenix", "dokku": False},
    {"archetype": "dokku-deployable-service", "primary_stack": "python-fastapi-uv-ruff-orjson-polars", "dokku": True},
    {"archetype": "data-pipeline", "primary_stack": "duckdb-trino-polars", "dokku": False},
    {"archetype": "local-rag-system", "primary_stack": "qdrant", "dokku": False},
    {"archetype": "multi-storage-experiment", "primary_stack": "redis-keydb-mongo", "dokku": False},
    {"archetype": "prompt-first-repo", "primary_stack": "prompt-first-repo", "dokku": False},
    # Four new backend-api-service stacks with manifests added in PROMPT_73.
    {"archetype": "backend-api-service", "primary_stack": "nim-jester-happyx", "dokku": False},
    {"archetype": "backend-api-service", "primary_stack": "scala-tapir-http4s-zio", "dokku": False},
    {"archetype": "backend-api-service", "primary_stack": "clojure-kit-nextjdbc-hiccup", "dokku": False},
    {"archetype": "backend-api-service", "primary_stack": "dart-dartfrog", "dokku": False},
    # Two new archetypes wired to their manifests in PROMPT_73.
    {"archetype": "data-acquisition-service", "primary_stack": "python-fastapi-uv-ruff-orjson-polars", "dokku": False},
    {"archetype": "multi-source-sync-platform", "primary_stack": "python-fastapi-uv-ruff-orjson-polars", "dokku": False},
    # Three new backend-api-service stacks with manifests added in PROMPT_75.
    {"archetype": "backend-api-service", "primary_stack": "crystal-kemal-avram", "dokku": False},
    {"archetype": "backend-api-service", "primary_stack": "ruby-hanami", "dokku": False},
    {"archetype": "backend-api-service", "primary_stack": "ocaml-dream-caqti-tyxml", "dokku": False},
)


def _extract_name(compose_text: str) -> str:
    """Return the Compose project name from a rendered Compose file."""

    match = re.search(r"^name:\s*(.+)$", compose_text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _extract_ports(compose_text: str) -> list[int]:
    """Return the host ports exposed in a rendered Compose file."""

    return [int(port) for port in re.findall(r'"(\d+):\d+"', compose_text)]


def _extract_volume_roots(compose_text: str) -> list[str]:
    """Return the local volume roots from a rendered Compose file."""

    return re.findall(r"^\s*-\s+(\./docker/volumes/[^\s:]+)", compose_text, flags=re.MULTILINE)


def _check_bootstrap_output(repo_root: Path) -> list[str]:
    """Generate sample repos and validate bootstrap invariants."""

    errors: list[str] = []
    for case in BOOTSTRAP_CASES:
        archetype = str(case["archetype"])
        primary_stack = str(case["primary_stack"])
        dokku = bool(case["dokku"])
        include_root_readme = bool(case.get("include_root_readme", False))
        include_docs_dir = bool(case.get("include_docs_dir", False))
        slug = f"check-{primary_stack}"
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / slug
            with Path(devnull).open("w", encoding="utf-8") as sink, redirect_stdout(sink):
                argv = [
                    "new_repo.py",
                    slug,
                    "--target-dir",
                    str(target_dir),
                    "--archetype",
                    archetype,
                    "--primary-stack",
                    primary_stack,
                    "--smoke-tests",
                    "--integration-tests",
                    "--seed-data",
                ]
                if dokku:
                    argv.append("--dokku")
                if include_root_readme:
                    argv.append("--include-root-readme")
                if include_docs_dir:
                    argv.append("--include-docs-dir")
                exit_code = new_repo.main(
                    argv
                )
            if exit_code != 0:
                errors.append(
                    f"bootstrap check failed for archetype={archetype} stack={primary_stack}: exit code {exit_code}"
                )
                continue

            prompt_first = primary_stack == "prompt-first-repo"
            if prompt_first:
                prompt_files = sorted(path.name for path in (target_dir / ".prompts").glob("*.txt"))
                classic = ["001-bootstrap-repo.txt", "002-refine-test-surface.txt"]
                derived = [f"PROMPT_{index:02d}.txt" for index in range(1, len(prompt_files) + 1)]
                if prompt_files and prompt_files != classic and prompt_files != derived:
                    errors.append(
                        f"{primary_stack}: prompt files must stay monotonic after bootstrap, saw {prompt_files}"
                    )
            if dokku:
                for required in ("Procfile", "app.json", "docs/deployment.md", "scripts/smoke/deploy_smoke.sh"):
                    if not (target_dir / required).exists():
                        errors.append(f"{primary_stack}: missing Dokku starter file '{required}'")
                if (target_dir / "README.md").exists() and not include_root_readme:
                    errors.append(f"{primary_stack}: Dokku support must not force a root README by default")

            docs_dir_generated = include_docs_dir or dokku
            readme_path = target_dir / "README.md"
            docs_dir = target_dir / "docs"
            if include_root_readme and not readme_path.exists():
                errors.append(f"{primary_stack}: --include-root-readme must generate README.md")
            if not include_root_readme and readme_path.exists():
                errors.append(f"{primary_stack}: root README.md must stay deferred by default")
            if docs_dir_generated and not docs_dir.exists():
                errors.append(f"{primary_stack}: docs directory must exist when explicitly requested or Dokku is enabled")
            if not docs_dir_generated and docs_dir.exists():
                errors.append(f"{primary_stack}: root docs directory must stay deferred by default")
            if include_docs_dir:
                for required in ("docs/repo-purpose.md", "docs/repo-layout.md"):
                    if not (target_dir / required).exists():
                        errors.append(f"{primary_stack}: missing opted-in repo docs file '{required}'")
            elif dokku:
                for unexpected in ("docs/repo-purpose.md", "docs/repo-layout.md"):
                    if (target_dir / unexpected).exists():
                        errors.append(f"{primary_stack}: Dokku support must not generate broad repo docs without --include-docs-dir")

            dev_compose = target_dir / "docker-compose.yml"
            test_compose = target_dir / "docker-compose.test.yml"
            if not dev_compose.exists() and not test_compose.exists():
                continue
            if not dev_compose.exists() or not test_compose.exists():
                errors.append(f"{primary_stack}: both dev and test Compose files must be generated together")
                continue

            dev_text = dev_compose.read_text(encoding="utf-8")
            test_text = test_compose.read_text(encoding="utf-8")
            dev_name = _extract_name(dev_text)
            test_name = _extract_name(test_text)
            if not dev_name or not test_name:
                errors.append(f"{primary_stack}: both Compose files must declare a top-level name")
            if dev_name == test_name:
                errors.append(f"{primary_stack}: dev and test Compose names must differ")
            if not test_name.endswith("-test"):
                errors.append(f"{primary_stack}: test Compose name must end with '-test'")

            dev_ports = _extract_ports(dev_text)
            test_ports = _extract_ports(test_text)
            if set(dev_ports) & set(test_ports):
                errors.append(
                    f"{primary_stack}: dev and test Compose files must not reuse host ports ({sorted(set(dev_ports) & set(test_ports))})"
                )

            dev_volume_roots = _extract_volume_roots(dev_text)
            test_volume_roots = _extract_volume_roots(test_text)
            if dev_volume_roots and not all(root.startswith("./docker/volumes/dev/") for root in dev_volume_roots):
                errors.append(f"{primary_stack}: dev Compose volumes must stay under ./docker/volumes/dev/")
            if test_volume_roots and not all(root.startswith("./docker/volumes/test/") for root in test_volume_roots):
                errors.append(f"{primary_stack}: test Compose volumes must stay under ./docker/volumes/test/")

            env_text = (target_dir / ".env").read_text(encoding="utf-8")
            env_test_text = (target_dir / ".env.test").read_text(encoding="utf-8")
            if env_text == env_test_text:
                errors.append(f"{primary_stack}: .env and .env.test must differ")
            if "APP_ENV=dev" not in env_text:
                errors.append(f"{primary_stack}: .env must declare APP_ENV=dev")
            if "APP_ENV=test" not in env_test_text:
                errors.append(f"{primary_stack}: .env.test must declare APP_ENV=test")
    return errors


def _check_derived_layout_output() -> list[str]:
    """Generate compact and maximal derived repos and verify their layout boundary."""

    errors: list[str] = []
    for mode in ("compact", "maximal"):
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            argv = [
                "new_repo.py",
                "--derived-example",
                "operator-surface",
                "--target-dir",
                str(parent),
            ]
            if mode == "maximal":
                argv.extend(["--derived-context-mode", "maximal"])
            with Path(devnull).open("w", encoding="utf-8") as sink, redirect_stdout(sink):
                exit_code = new_repo.main(argv)
            if exit_code != 0:
                errors.append(f"derived bootstrap check failed for mode={mode}: exit code {exit_code}")
                continue

            target_dir = parent / "operator-surface"
            profile_path = target_dir / ".acb" / "manifests" / "project-profile.yaml"
            if not profile_path.exists():
                errors.append(f"derived mode={mode}: missing .acb/manifests/project-profile.yaml")
                continue
            profile_text = profile_path.read_text(encoding="utf-8")
            required = (
                ".acb/.generated-profile.yaml",
                ".acb/manifests/base/prompt-first-meta-repo.yaml",
                ".acb/context/doctrine/core-principles.md",
                ".acb/scripts/validate_repo.py",
                ".acb/docs/seams/README.md",
            )
            for relative_path in required:
                if not (target_dir / relative_path).exists():
                    errors.append(f"derived mode={mode}: missing {relative_path}")
            for leaked_root in ("context", "examples", "templates", "docs", "scripts", "manifests"):
                if (target_dir / leaked_root).exists():
                    errors.append(f"derived mode={mode}: root {leaked_root}/ must stay hidden under .acb/")
            public_root = {path.name for path in target_dir.iterdir() if not path.name.startswith(".")}
            if public_root != {"AGENT.md", "CLAUDE.md"}:
                errors.append(f"derived mode={mode}: public root entries must be only AGENT.md and CLAUDE.md, saw {sorted(public_root)}")
            if "generated_profile_path: .acb/.generated-profile.yaml" not in profile_text:
                errors.append(f"derived mode={mode}: profile must record .acb/.generated-profile.yaml")
            if "repo_local_profile_path: .acb/manifests/project-profile.yaml" not in profile_text:
                errors.append(f"derived mode={mode}: profile must record .acb/manifests/project-profile.yaml")
            if "vendored_base_root: .acb" not in profile_text:
                errors.append(f"derived mode={mode}: profile must record vendored_base_root: .acb")
    return errors


def main() -> int:
    """Run full context validation."""

    repo_root = Path(__file__).resolve().parents[1]
    manifest_dir = repo_root / "manifests"
    manifest_paths = sorted(manifest_dir.glob("*.yaml"))

    errors: list[str] = []
    for manifest_path in manifest_paths:
        errors.extend(validate_manifest(repo_root, manifest_path))
    errors.extend(validate_context_weights(repo_root))
    errors.extend(validate_example_catalog(repo_root))
    errors.extend(validate_data_acquisition_consistency(repo_root))
    errors.extend(validate_repo_signal_hints(repo_root))
    errors.extend(validate_prompt_numbering(repo_root))
    errors.extend(validate_markdown_cross_references(repo_root))
    errors.extend(validate_mermaid_reference_hints(repo_root))
    errors.extend(_check_bootstrap_output(repo_root))
    errors.extend(_check_derived_layout_output())

    if errors:
        print("Context validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Validated {len(manifest_paths)} manifests, context metadata, prompt numbering, and bootstrap invariants."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
