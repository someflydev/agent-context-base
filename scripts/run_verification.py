#!/usr/bin/env python3
"""Run repository verification by tier with optional stack and example filters."""

from __future__ import annotations

import argparse
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import verify_examples  # noqa: E402


FAST_MODULES = [
    "verification.unit.test_acb_payload",
    "verification.unit.test_repo_integrity",
    "verification.unit.test_prompt_rules",
    "verification.unit.test_manifests",
    "verification.unit.test_alias_catalog",
    "verification.scripts.test_repo_scripts",
    "verification.examples.data.test_yaml_json_examples",
    "verification.examples.data.test_storage_examples",
    # Terminal example smoke suites are expected to join the fast tier as
    # concrete examples land in PROMPT_102 through PROMPT_105.
]

MEDIUM_MODULES = FAST_MODULES + [
    "verification.examples.python.test_fastapi_examples",
    "verification.examples.python.test_polars_examples",
    "verification.examples.python.test_cli_examples",
]

HEAVY_MODULES = MEDIUM_MODULES + [
    "verification.examples.nim.test_nim_jester_happyx_examples",
    "verification.examples.scala.test_scala_tapir_http4s_zio_examples",
    "verification.examples.kotlin.test_http4k_exposed_examples",
    "verification.examples.dart.test_dart_dartfrog_examples",
    "verification.examples.clojure.test_kit_nextjdbc_hiccup_examples",
    "verification.examples.ocaml.test_ocaml_dream_caqti_tyxml_examples",
    "verification.examples.zig.test_zig_zap_jetzig_examples",
    "verification.examples.go.test_echo_examples",
    "verification.examples.rust.test_axum_examples",
    "verification.examples.elixir.test_phoenix_examples",
    "verification.examples.ruby.test_ruby_hanami_examples",
    "verification.examples.typescript.test_typescript_examples",
    "verification.examples.typescript.test_hono_data_acquisition_examples",
    "verification.examples.data.test_data_acquisition_examples",
    "verification.examples.derived.test_derived_coverage",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run repository verification by tier.")
    parser.add_argument(
        "--tier",
        choices=("fast", "medium", "heavy", "all"),
        default="fast",
        help="Verification tier to run.",
    )
    parser.add_argument("--stack", action="append", default=[], help="Filter example suites by stack.")
    parser.add_argument("--example", action="append", default=[], help="Filter example suites by example name.")
    parser.add_argument("--docker", action="store_true", help="Enable Docker-backed smoke checks.")
    parser.add_argument("--list", action="store_true", help="Print the selected test modules and exit.")
    return parser


def modules_for_tier(tier: str) -> list[str]:
    if tier == "fast":
        return list(FAST_MODULES)
    if tier == "medium":
        return list(MEDIUM_MODULES)
    return list(HEAVY_MODULES)


def run_modules(modules: list[str]) -> unittest.result.TestResult:
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for module in modules:
        suite.addTests(loader.loadTestsFromName(module))
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv[1:])

    if args.docker:
        os.environ["VERIFY_DOCKER"] = "1"

    if args.stack or args.example:
        modules = verify_examples.collect_modules(verify_examples.filtered_entries(args.stack, args.example))
        if args.tier == "fast":
            modules = FAST_MODULES + [module for module in modules if module.startswith("verification.examples.")]
        elif args.tier in {"medium", "heavy", "all"}:
            modules = modules_for_tier("heavy" if args.tier in {"heavy", "all"} else "medium")
            selected = verify_examples.collect_modules(verify_examples.filtered_entries(args.stack, args.example))
            modules = FAST_MODULES + [module for module in selected if module not in FAST_MODULES]
    else:
        modules = modules_for_tier("heavy" if args.tier in {"heavy", "all"} else args.tier)

    if args.list:
        for module in modules:
            print(module)
        return 0

    result = run_modules(modules)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
