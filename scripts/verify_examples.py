#!/usr/bin/env python3
"""Run canonical example verification selectively by stack or example."""

from __future__ import annotations

import argparse
import json
import os
import sys
import unittest
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from verification.helpers import load_registry, verification_score, confidence_score  # noqa: E402


DEFAULT_MODULES = [
    "verification.examples.python.test_fastapi_examples",
    "verification.examples.python.test_polars_examples",
    "verification.examples.python.test_cli_examples",
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
    "verification.examples.data.test_yaml_json_examples",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run canonical example verification selectively.")
    parser.add_argument("--stack", action="append", default=[], help="Filter by stack tag. May be repeated.")
    parser.add_argument("--example", action="append", default=[], help="Filter by example name. May be repeated.")
    parser.add_argument("--docker", action="store_true", help="Enable Docker-backed smoke checks.")
    parser.add_argument("--list", action="store_true", help="List available registry entries and exit.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable selection metadata.")
    return parser


def filtered_entries(stacks: list[str], examples: list[str]) -> list[dict[str, object]]:
    selected: list[dict[str, object]] = []
    wanted_stacks = {item.strip() for item in stacks if item.strip()}
    wanted_examples = {item.strip() for item in examples if item.strip()}
    for entry in load_registry():
        entry_name = str(entry.get("name", ""))
        entry_stacks = {str(item) for item in entry.get("stack_tags", []) if isinstance(item, str)}
        if wanted_stacks and not entry_stacks & wanted_stacks:
            continue
        if wanted_examples and entry_name not in wanted_examples:
            continue
        selected.append(entry)
    return selected


def modules_for_entry(entry: dict[str, object]) -> list[str]:
    path = str(entry.get("path", ""))
    language = str(entry.get("language", ""))
    if "fastapi" in path:
        return ["verification.examples.python.test_fastapi_examples"]
    if "canonical-cli" in path:
        return ["verification.examples.python.test_cli_examples"]
    if "canonical-storage" in path or "canonical-seed-data" in path:
        return ["verification.examples.python.test_polars_examples"]
    if language == "nim":
        return ["verification.examples.nim.test_nim_jester_happyx_examples"]
    if language == "scala":
        return ["verification.examples.scala.test_scala_tapir_http4s_zio_examples"]
    if language == "kotlin":
        return ["verification.examples.kotlin.test_http4k_exposed_examples"]
    if language == "dart":
        return ["verification.examples.dart.test_dart_dartfrog_examples"]
    if language == "clojure":
        return ["verification.examples.clojure.test_kit_nextjdbc_hiccup_examples"]
    if language == "ocaml":
        return ["verification.examples.ocaml.test_ocaml_dream_caqti_tyxml_examples"]
    if language == "zig":
        return ["verification.examples.zig.test_zig_zap_jetzig_examples"]
    if language == "go":
        return ["verification.examples.go.test_echo_examples"]
    if language == "rust":
        return ["verification.examples.rust.test_axum_examples"]
    if language == "elixir":
        return ["verification.examples.elixir.test_phoenix_examples"]
    if language in {"yaml", "json"} or "canonical-dokku" in path or "canonical-observability" in path:
        return ["verification.examples.data.test_yaml_json_examples"]
    if "canonical-prompts" in path:
        return ["verification.unit.test_prompt_rules"]
    return []


def collect_modules(entries: list[dict[str, object]]) -> list[str]:
    if not entries:
        return list(DEFAULT_MODULES)
    modules: list[str] = []
    for entry in entries:
        for module in modules_for_entry(entry):
            if module not in modules:
                modules.append(module)
    return modules


def run_modules(modules: Iterable[str]) -> unittest.result.TestResult:
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for module in modules:
        suite.addTests(loader.loadTestsFromName(module))
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv[1:])

    entries = filtered_entries(args.stack, args.example)
    modules = collect_modules(entries)
    if args.docker:
        os.environ["VERIFY_DOCKER"] = "1"

    if args.list:
        payload = [
            {
                "name": entry.get("name"),
                "path": entry.get("path"),
                "verification_level": entry.get("verification_level"),
                "confidence": entry.get("confidence"),
            }
            for entry in (entries or load_registry())
        ]
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            for item in payload:
                print(
                    f"{item['name']}: {item['path']} "
                    f"[level={item['verification_level']}, confidence={item['confidence']}]"
                )
        return 0

    report = {
        "selected_examples": [
            {
                "name": entry.get("name"),
                "path": entry.get("path"),
                "verification_level": entry.get("verification_level"),
                "confidence": entry.get("confidence"),
                "preference_score": verification_score(entry) * 10 + confidence_score(entry),
            }
            for entry in entries
        ],
        "modules": modules,
    }
    if args.json:
        print(json.dumps(report, indent=2))

    result = run_modules(modules)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
