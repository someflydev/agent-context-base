from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT
from verification.scenarios.ocaml_dream_caqti_tyxml_min_app.verify import docker_smoke_check


API_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/ocaml-dream-caqti-tyxml-api-endpoint-example.ml"
FRAGMENT_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/ocaml-dream-caqti-tyxml-html-fragment-example.ml"
DATA_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/ocaml-dream-caqti-tyxml-data-endpoint-example.ml"
DATA_ACQUISITION_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-data-acquisition/ocaml-dream-source-sync-example.ml"
DATA_ACQUISITION_README_PATH = REPO_ROOT / "examples/canonical-data-acquisition/README.md"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/ocaml-dream-caqti-tyxml-example"


class OcamlDreamCaqtiTyxmlExampleTests(unittest.TestCase):
    def test_api_example_contains_dream_and_caqti_surface(self) -> None:
        text = API_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('Dream.get "/api/reports/:tenant_id"', text)
        self.assertIn("open Caqti_request.Infix", text)
        self.assertIn("->*", text)
        self.assertIn('Dream.query request "limit"', text)

    def test_fragment_example_contains_tyxml_fragment_surface(self) -> None:
        text = FRAGMENT_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("let open Tyxml.Html in", text)
        self.assertIn('Dream.get "/fragments/report-card/:tenant_id"', text)
        self.assertIn('Unsafe.string_attrib "hx-swap-oob" "true"', text)

    def test_data_example_contains_chart_payload_surface(self) -> None:
        text = DATA_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('Dream.get "/data/chart/:metric"', text)
        self.assertIn("open Caqti_request.Infix", text)
        self.assertIn("->*", text)
        self.assertIn('("metric", `String metric)', text)

    def test_data_acquisition_example_contains_expected_sync_markers(self) -> None:
        text = DATA_ACQUISITION_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("let select_checkpoint =", text)
        self.assertIn("archive_raw_capture", text)
        self.assertIn("let replay_from_archive", text)
        self.assertIn('Dream.post "/source-sync/:owner/:repo"', text)
        self.assertIn("let open Tyxml.Html in", text)
        self.assertIn("checkpoint_token", text)

    def test_data_acquisition_readme_references_ocaml_example_honestly(self) -> None:
        text = DATA_ACQUISITION_README_PATH.read_text(encoding="utf-8")
        self.assertIn("ocaml-dream-source-sync-example.ml (structure-verified)", text)
        self.assertIn("real OCaml example, `structure-verified` only", text)

    def test_runtime_bundle_files_exist(self) -> None:
        for relative in ("dune-project", "ocaml-dream-caqti-tyxml-example.opam", "Dockerfile", "README.md", "bin/main.ml", "bin/dune"):
            with self.subTest(relative=relative):
                self.assertTrue((RUNTIME_DIR / relative).exists())

    def test_optional_docker_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["health_status"], 200)
        self.assertEqual(
            payload["health_payload"],
            {"status": "ok", "service": "ocaml-dream-caqti-tyxml-example"},
        )
        self.assertEqual(payload["api_status"], 200)
        self.assertEqual(payload["api_payload"]["tenant_id"], "acme")
        self.assertEqual(payload["data_status"], 200)
        self.assertEqual(payload["data_payload"]["metric"], "signups")
        self.assertEqual(payload["fragment_status"], 200)
        self.assertIn('class="report-card"', payload["fragment_payload"])


if __name__ == "__main__":
    unittest.main()
