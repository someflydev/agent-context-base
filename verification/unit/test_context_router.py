from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT, run_command


sys.path.insert(0, str(REPO_ROOT / "scripts"))

from context_router import infer_route, suggest_context_bundle  # noqa: E402


PYTHON = sys.executable
WORK_SCRIPT = REPO_ROOT / "scripts" / "work.py"

SCENARIO_1_PROMPT = (
    "Add a paginated GET /products endpoint to the FastAPI service that queries "
    "a Postgres table and returns results with next_cursor for keyset pagination."
)
SCENARIO_2_PROMPT = (
    "Compare Qdrant versus Meilisearch for semantic search latency over 50K "
    "product documents. Index the same dataset in both, run 20 queries, "
    "measure p50 and p95 latency, and produce a short report."
)
SCENARIO_3_PROMPT = (
    "Bootstrap a new data acquisition service that scrapes product prices from "
    "3 e-commerce sites on a daily schedule, stores raw HTML in S3-compatible "
    "storage, transforms prices into a Polars dataframe stored in DuckDB, "
    "exposes a FastAPI /prices endpoint with Postgres persistence, and "
    "deploys to Dokku."
)


def run_work_command(*args: str) -> tuple[int, str, str]:
    result = run_command([PYTHON, str(WORK_SCRIPT), *args], cwd=REPO_ROOT, timeout=240)
    return result.returncode, result.stdout, result.stderr


class TestKeywordCapabilityMatching(unittest.TestCase):
    def test_api_keywords_match_api_capability(self) -> None:
        result = infer_route("Add a REST API endpoint for user login", REPO_ROOT)
        self.assertIn("api", result.implied_capabilities)

    def test_storage_keywords_match_storage(self) -> None:
        result = infer_route("Store results in Postgres and DuckDB", REPO_ROOT)
        self.assertIn("storage", result.implied_capabilities)

    def test_rag_keywords_match_rag_capability(self) -> None:
        result = infer_route("Index documents into Qdrant for semantic search", REPO_ROOT)
        self.assertIn("rag", result.implied_capabilities)

    def test_empty_prompt_low_confidence(self) -> None:
        result = infer_route("", REPO_ROOT)
        self.assertLess(result.confidence, 0.55)

    def test_multi_capability_detection(self) -> None:
        result = infer_route("scrape prices, store in postgres, expose API, deploy to dokku", REPO_ROOT)
        self.assertTrue(result.is_multi_capability)


class TestRouteInference(unittest.TestCase):
    def test_scenario_1_simple_api(self) -> None:
        result = infer_route(SCENARIO_1_PROMPT, REPO_ROOT)
        self.assertEqual(result.primary_archetype, "backend-api-service")
        self.assertIn(result.suggested_budget_profile, {"small", "medium"})
        self.assertGreaterEqual(result.confidence, 0.70)
        bundle = suggest_context_bundle(result, REPO_ROOT)
        self.assertIn("manifests/backend-api-fastapi-polars.yaml", bundle)

    def test_scenario_2_rag_comparison(self) -> None:
        result = infer_route(SCENARIO_2_PROMPT, REPO_ROOT)
        self.assertIn("rag", result.implied_capabilities)
        self.assertTrue(result.is_likely_juicy)
        self.assertIn(result.suggested_budget_profile, {"large", "cross-system"})

    def test_scenario_3_full_stack(self) -> None:
        result = infer_route(SCENARIO_3_PROMPT, REPO_ROOT)
        self.assertGreaterEqual(len(result.implied_capabilities), 4)
        self.assertEqual(result.suggested_budget_profile, "cross-system")
        self.assertTrue(result.is_likely_juicy)
        self.assertEqual(result.primary_archetype, "data-acquisition-service")


class TestRouteCheckCommand(unittest.TestCase):
    def test_route_check_produces_output(self) -> None:
        code, stdout, stderr = run_work_command("route-check", "add an API endpoint")
        self.assertEqual(code, 0, stderr)
        self.assertIn("Route Check", stdout)
        self.assertIn("HEURISTIC", stdout)

    def test_route_check_json_flag(self) -> None:
        code, stdout, stderr = run_work_command("route-check", "--json", "add an API endpoint")
        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        self.assertIn("implied_capabilities", payload)
        self.assertIn("primary_archetype", payload)
        self.assertTrue(payload["heuristic"])

    def test_route_check_file_input(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as handle:
            handle.write("add an API endpoint")
            prompt_path = Path(handle.name)
        try:
            code, stdout, stderr = run_work_command("route-check", f"@{prompt_path}")
            self.assertEqual(code, 0, stderr)
            self.assertIn("Route Check", stdout)
        finally:
            prompt_path.unlink(missing_ok=True)

    def test_route_check_compare_bundle(self) -> None:
        code, stdout, stderr = run_work_command(
            "route-check",
            "--compare-bundle",
            "AGENT.md",
            "add an API endpoint",
        )
        self.assertEqual(code, 0, stderr)
        self.assertIn("Bundle Comparison", stdout)

    def test_route_check_juicy_prompt_warning(self) -> None:
        code, stdout, stderr = run_work_command("route-check", SCENARIO_3_PROMPT)
        self.assertEqual(code, 0, stderr)
        self.assertIn("HEURISTIC", stdout)
        self.assertIn("api, storage, pipelines, scraping", stdout)

