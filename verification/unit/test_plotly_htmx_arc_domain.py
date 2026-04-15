import unittest
import os
import json
from pathlib import Path

class TestAnalyticsDomainSpec(unittest.TestCase):
    def setUp(self):
        self.spec_path = Path("examples/canonical-analytics/domain/spec.md")

    def test_spec_file_exists(self):
        self.assertTrue(self.spec_path.exists())

    def test_spec_has_all_six_chart_families(self):
        content = self.spec_path.read_text()
        for i in range(1, 7):
            self.assertIn(f"Family {i}", content)

    def test_spec_has_workbench_routes_section(self):
        content = self.spec_path.read_text()
        self.assertIn("The Workbench Layout", content)
        self.assertIn("/trends", content)
        self.assertIn("/services", content)

    def test_spec_has_parity_contract_section(self):
        content = self.spec_path.read_text()
        self.assertIn("Parity Contract", content)

class TestSeedDataContract(unittest.TestCase):
    def setUp(self):
        self.contract_path = Path("examples/canonical-analytics/domain/seed-data-contract.md")

    def test_contract_file_exists(self):
        self.assertTrue(self.contract_path.exists())

    def test_contract_mentions_smoke_profile(self):
        content = self.contract_path.read_text()
        self.assertIn("smoke", content)

    def test_contract_references_faker_arc(self):
        content = self.contract_path.read_text()
        self.assertIn("canonical-faker", content)

class TestParityMatrix(unittest.TestCase):
    def setUp(self):
        self.matrix_path = Path("examples/canonical-analytics/domain/parity-matrix.md")

    def test_parity_matrix_exists(self):
        self.assertTrue(self.matrix_path.exists())

    def test_parity_matrix_has_all_four_stacks(self):
        content = self.matrix_path.read_text()
        self.assertIn("Python", content)
        self.assertIn("Go", content)
        self.assertIn("Rust", content)
        self.assertIn("Elixir", content)

    def test_parity_matrix_has_all_six_chart_families(self):
        content = self.matrix_path.read_text()
        self.assertIn("Time Series", content)
        self.assertIn("Category Comparison", content)
        self.assertIn("Distribution", content)
        self.assertIn("Heatmap", content)
        self.assertIn("Funnel", content)
        self.assertIn("Incident Distribution", content)

class TestVerificationContract(unittest.TestCase):
    def setUp(self):
        self.contract_path = Path("examples/canonical-analytics/domain/verification-contract.md")

    def test_contract_file_exists(self):
        self.assertTrue(self.contract_path.exists())

    def test_contract_has_smoke_test_section(self):
        content = self.contract_path.read_text()
        self.assertIn("Smoke Tests", content)

    def test_contract_has_figure_builder_unit_test_section(self):
        content = self.contract_path.read_text()
        self.assertIn("Figure Builder Unit Tests", content)

    def test_contract_has_filter_alignment_section(self):
        content = self.contract_path.read_text()
        self.assertIn("Filter State Alignment", content)

class TestPageLayoutSpec(unittest.TestCase):
    def setUp(self):
        self.layout_path = Path("examples/canonical-analytics/domain/page-layout-spec.md")

    def test_layout_spec_exists(self):
        self.assertTrue(self.layout_path.exists())

    def test_layout_spec_has_filter_panel_section(self):
        content = self.layout_path.read_text()
        self.assertIn("Filter Panel", content)

    def test_layout_spec_references_filter_panel_rendering_rules(self):
        content = self.layout_path.read_text()
        self.assertIn("filter-panel-rendering-rules", content)

class TestCatalogSkeleton(unittest.TestCase):
    def setUp(self):
        self.catalog_path = Path("examples/canonical-analytics/CATALOG.md")

    def test_catalog_exists(self):
        self.assertTrue(self.catalog_path.exists())

    def test_catalog_has_all_four_implementations(self):
        content = self.catalog_path.read_text()
        self.assertIn("Python", content)
        self.assertIn("Go", content)
        self.assertIn("Rust", content)
        self.assertIn("Elixir", content)

    def test_catalog_references_faker_arc(self):
        content = self.catalog_path.read_text()
        self.assertIn("canonical-faker", content)

class TestFixtureFiles(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = Path("examples/canonical-analytics/domain/fixtures")

    def test_smoke_fixture_exists(self):
        self.assertTrue((self.fixtures_dir / "smoke.json").exists())

    def test_smoke_fixture_is_valid_json(self):
        with open(self.fixtures_dir / "smoke.json") as f:
            data = json.load(f)
            self.assertIsInstance(data, dict)

    def test_smoke_fixture_has_required_keys(self):
        with open(self.fixtures_dir / "smoke.json") as f:
            data = json.load(f)
            keys = ["events", "sessions", "services", "deployments", "incidents", "latency_samples", "funnel_stages"]
            for key in keys:
                self.assertIn(key, data)

    def test_small_fixture_exists(self):
        self.assertTrue((self.fixtures_dir / "small.json").exists())

    def test_small_fixture_is_valid_json(self):
        with open(self.fixtures_dir / "small.json") as f:
            data = json.load(f)
            self.assertIsInstance(data, dict)

    def test_fixture_generator_script_exists(self):
        self.assertTrue(Path("examples/canonical-analytics/domain/generate_fixtures.py").exists())

class TestGeneratorDogfooding(unittest.TestCase):
    def test_generator_references_canonical_faker(self):
        content = Path("examples/canonical-analytics/domain/generate_fixtures.py").read_text()
        self.assertIn("canonical-faker", content)

if __name__ == '__main__':
    unittest.main()
