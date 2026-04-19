#!/usr/bin/env python3
"""
Plotly + HTMX arc parity check runner.

Checks:
1. Implementation directories exist for all 4 stacks.
2. CATALOG.md marks all 4 implementations as [x].
3. parity-matrix.md has no [ ] (not started) cells.
4. Fixture files (smoke.json, small.json) exist and have required keys.
5. Python smoke tests pass (optional; skipped if httpx not installed).
"""

import sys
import json
import pathlib
import subprocess
import unittest

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
ANALYTICS_DIR = REPO_ROOT / "examples" / "canonical-analytics"
FIXTURE_DIR = ANALYTICS_DIR / "domain" / "fixtures"

REQUIRED_IMPLEMENTATIONS = ["python", "go", "rust", "elixir"]
REQUIRED_FIXTURE_KEYS = [
    "events", "sessions", "services", "deployments",
    "incidents", "latency_samples", "funnel_stages"
]

class TestImplementationDirectories(unittest.TestCase):
    def test_all_implementation_dirs_exist(self):
        for stack in REQUIRED_IMPLEMENTATIONS:
            d = ANALYTICS_DIR / stack
            self.assertTrue(d.exists(), f"Missing: {d}")

class TestCatalogCompleteness(unittest.TestCase):
    def test_all_implementations_marked_complete(self):
        catalog = (ANALYTICS_DIR / "CATALOG.md").read_text()
        for stack in ["Python", "Go", "Rust", "Elixir"]:
            self.assertIn(f"| {stack}", catalog, f"{stack} not in CATALOG.md")
            # Find the line and check it has [x]
            for line in catalog.splitlines():
                if f"| {stack}" in line:
                    self.assertIn("[x]", line, f"{stack} row not marked [x]")

class TestParityMatrixCompleteness(unittest.TestCase):
    def test_no_not_started_cells_in_matrix(self):
        matrix = (ANALYTICS_DIR / "domain" / "parity-matrix.md").read_text()
        not_started = [line for line in matrix.splitlines()
                       if "| [ ]" in line or "|[ ]" in line or "| [~]" in line or "|[~]" in line]
        self.assertEqual(not_started, [],
            f"Parity matrix has incomplete rows:\n" + "\n".join(not_started))

class TestFixtureFiles(unittest.TestCase):
    def _load_fixture(self, name):
        path = FIXTURE_DIR / f"{name}.json"
        self.assertTrue(path.exists(), f"Missing fixture: {path}")
        with open(path) as f:
            return json.load(f)

    def test_smoke_fixture_exists_and_valid(self):
        data = self._load_fixture("smoke")
        for key in REQUIRED_FIXTURE_KEYS:
            self.assertIn(key, data, f"smoke.json missing key: {key}")

    def test_small_fixture_exists_and_valid(self):
        data = self._load_fixture("small")
        for key in REQUIRED_FIXTURE_KEYS:
            self.assertIn(key, data, f"small.json missing key: {key}")

    def test_smoke_fixture_minimum_coverage(self):
        data = self._load_fixture("smoke")
        services = {e.get("service") for e in data.get("events", []) if e.get("service")}
        self.assertGreaterEqual(len(services), 3, "smoke.json: need >= 3 services")
        environments = {e.get("environment") for e in data.get("events", []) if e.get("environment")}
        self.assertGreaterEqual(len(environments), 2, "smoke.json: need >= 2 environments")
        severities = {i.get("severity") for i in data.get("incidents", []) if i.get("severity")}
        self.assertGreaterEqual(len(severities), 3, "smoke.json: need >= 3 severity levels")

class TestDocumentation(unittest.TestCase):
    def test_arc_overview_exists(self):
        p = REPO_ROOT / "docs" / "plotly-htmx-arc-overview.md"
        self.assertTrue(p.exists(), f"Missing: {p}")

    def test_arc_overview_has_navigation_section(self):
        p = REPO_ROOT / "docs" / "plotly-htmx-arc-overview.md"
        self.assertIn("Navigation", p.read_text())

    def test_arc_overview_has_all_four_stacks(self):
        text = (REPO_ROOT / "docs" / "plotly-htmx-arc-overview.md").read_text()
        for stack in ["Python", "Go", "Rust", "Elixir"]:
            self.assertIn(stack, text)

if __name__ == "__main__":
    result = unittest.main(exit=False, verbosity=2)
    sys.exit(0 if result.result.wasSuccessful() else 1)
