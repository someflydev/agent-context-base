from __future__ import annotations

import json
import unittest
from pathlib import Path

from verification.terminal.harness import REPO_ROOT


FIXTURES_ROOT = REPO_ROOT / "examples/canonical-schema-validation/domain/fixtures"
VALID_DIR = FIXTURES_ROOT / "valid"
INVALID_DIR = FIXTURES_ROOT / "invalid"
EDGE_DIR = FIXTURES_ROOT / "edge"

VALID_FILES = {
    "workspace_config_basic.json",
    "workspace_config_full.json",
    "sync_run_pending.json",
    "sync_run_succeeded.json",
    "webhook_payload_sync_completed.json",
    "webhook_payload_sync_failed.json",
    "webhook_payload_workspace_suspended.json",
    "ingestion_source_http_poll.json",
    "ingestion_source_webhook_push.json",
    "review_request_normal.json",
    "review_request_critical.json",
}

INVALID_FILES = {
    "workspace_config_bad_slug.json",
    "workspace_config_plan_too_many_runs.json",
    "sync_run_timestamps_inverted.json",
    "sync_run_duration_missing_when_finished.json",
    "webhook_payload_bad_signature_format.json",
    "ingestion_source_poll_interval_missing.json",
    "review_request_no_reviewers.json",
    "review_request_critical_no_due_date.json",
}

EDGE_FILES = {
    "workspace_config_max_tags.json",
    "sync_run_zero_records.json",
    "webhook_payload_unknown_event_type.json",
    "review_request_duplicate_content_ids.json",
}


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class TestFixtureCorpusExists(unittest.TestCase):
    def test_valid_fixtures_exist(self) -> None:
        self.assertEqual({path.name for path in VALID_DIR.glob("*.json")}, VALID_FILES)

    def test_invalid_fixtures_exist(self) -> None:
        self.assertEqual({path.name for path in INVALID_DIR.glob("*.json")}, INVALID_FILES)

    def test_edge_fixtures_exist(self) -> None:
        self.assertEqual({path.name for path in EDGE_DIR.glob("*.json")}, EDGE_FILES)


class TestFixtureCorpusIsValidJSON(unittest.TestCase):
    def test_all_valid_fixtures_parse(self) -> None:
        for path in sorted(VALID_DIR.glob("*.json")):
            self.assertIsNotNone(load_json(path), path.name)

    def test_all_invalid_fixtures_parse(self) -> None:
        for path in sorted(INVALID_DIR.glob("*.json")):
            self.assertIsNotNone(load_json(path), path.name)

    def test_all_edge_fixtures_parse(self) -> None:
        for path in sorted(EDGE_DIR.glob("*.json")):
            self.assertIsNotNone(load_json(path), path.name)


class TestFixtureCorpusContent(unittest.TestCase):
    def test_workspace_config_basic_has_required_fields(self) -> None:
        fixture = load_json(VALID_DIR / "workspace_config_basic.json")
        self.assertEqual(
            set(fixture.keys()),
            {
                "id",
                "name",
                "slug",
                "owner_email",
                "plan",
                "max_sync_runs",
                "settings",
                "tags",
                "created_at",
                "suspended_until",
            },
        )

    def test_sync_run_succeeded_has_timestamps(self) -> None:
        fixture = load_json(VALID_DIR / "sync_run_succeeded.json")
        self.assertIsInstance(fixture["started_at"], str)
        self.assertIsInstance(fixture["finished_at"], str)
        self.assertIsInstance(fixture["duration_ms"], int)

    def test_sync_run_pending_timestamps_are_null(self) -> None:
        fixture = load_json(VALID_DIR / "sync_run_pending.json")
        self.assertIsNone(fixture["started_at"])
        self.assertIsNone(fixture["finished_at"])
        self.assertIsNone(fixture["duration_ms"])

    def test_invalid_slug_fixture_has_bad_slug(self) -> None:
        fixture = load_json(INVALID_DIR / "workspace_config_bad_slug.json")
        self.assertRegex(fixture["slug"], r"[^a-z0-9-]|\s")

    def test_invalid_critical_no_due_date(self) -> None:
        fixture = load_json(INVALID_DIR / "review_request_critical_no_due_date.json")
        self.assertEqual(fixture["priority"], "critical")
        self.assertIsNone(fixture["due_at"])

    def test_webhook_discriminated_union_structure(self) -> None:
        for path in sorted(VALID_DIR.glob("webhook_payload_*.json")):
            fixture = load_json(path)
            self.assertIn("event_type", fixture)
            self.assertIsInstance(fixture["data"], dict)


if __name__ == "__main__":
    unittest.main()
