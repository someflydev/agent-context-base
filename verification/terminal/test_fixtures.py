from __future__ import annotations

import json
import unittest
from pathlib import Path

from verification.terminal.harness import REPO_ROOT


class TestFixtureCorpus(unittest.TestCase):
    def setUp(self) -> None:
        self.fixtures_dir = REPO_ROOT / "examples/canonical-terminal/fixtures"
        with (self.fixtures_dir / "jobs.json").open(encoding="utf-8") as handle:
            self.jobs = json.load(handle)
        with (self.fixtures_dir / "events.json").open(encoding="utf-8") as handle:
            self.events = json.load(handle)
        with (self.fixtures_dir / "jobs-large.json").open(encoding="utf-8") as handle:
            self.jobs_large = json.load(handle)
        with (self.fixtures_dir / "events-large.json").open(encoding="utf-8") as handle:
            self.events_large = json.load(handle)

    def test_jobs_count(self) -> None:
        self.assertEqual(len(self.jobs), 20)

    def test_jobs_large_count(self) -> None:
        self.assertEqual(len(self.jobs_large), 100)

    def test_events_count(self) -> None:
        self.assertEqual(len(self.events), 30)

    def test_events_large_count(self) -> None:
        self.assertEqual(len(self.events_large), 300)

    def test_jobs_have_required_fields(self) -> None:
        required = {"id", "name", "status", "tags", "output_lines"}
        for job in self.jobs:
            self.assertTrue(required.issubset(job.keys()), f"job {job.get('id')} missing fields")

    def test_jobs_large_have_required_fields(self) -> None:
        required = {"id", "name", "status", "started_at", "duration_s", "tags", "output_lines"}
        for job in self.jobs_large:
            self.assertTrue(required.issubset(job.keys()), f"job {job.get('id')} missing fields")

    def test_job_statuses_valid(self) -> None:
        valid = {"pending", "running", "done", "failed"}
        for job in self.jobs:
            self.assertIn(job["status"], valid)
        for job in self.jobs_large:
            self.assertIn(job["status"], valid)

    def test_jobs_have_unique_ids(self) -> None:
        ids = [job["id"] for job in self.jobs]
        self.assertEqual(len(ids), len(set(ids)))

    def test_jobs_large_have_unique_ids(self) -> None:
        ids = [job["id"] for job in self.jobs_large]
        self.assertEqual(len(ids), len(set(ids)))

    def test_events_reference_valid_jobs(self) -> None:
        job_ids = {job["id"] for job in self.jobs}
        for event in self.events:
            self.assertIn(event["job_id"], job_ids, f"event {event.get('event_id')} references unknown job {event.get('job_id')}")

    def test_events_large_reference_valid_jobs(self) -> None:
        job_ids = {job["id"] for job in self.jobs_large}
        for event in self.events_large:
            self.assertIn(event["job_id"], job_ids, f"event {event.get('event_id')} references unknown job {event.get('job_id')}")

    def test_large_events_are_chronologically_sorted(self) -> None:
        timestamps = [event["timestamp"] for event in self.events_large]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_done_jobs_have_duration(self) -> None:
        for job in self.jobs:
            if job["status"] == "done":
                self.assertIsNotNone(job.get("duration_s"), f"done job {job['id']} missing duration_s")

    def test_pending_jobs_have_no_started_at(self) -> None:
        for job in self.jobs:
            if job["status"] == "pending":
                self.assertIsNone(job.get("started_at"), f"pending job {job['id']} should not have started_at")

    def test_large_jobs_match_expected_status_distribution(self) -> None:
        counts = {status: sum(1 for job in self.jobs_large if job["status"] == status) for status in {"done", "failed", "running", "pending"}}
        self.assertEqual(counts, {"done": 30, "failed": 15, "running": 20, "pending": 35})

    def test_large_jobs_have_exact_unicode_tag_count(self) -> None:
        unicode_jobs = [
            job
            for job in self.jobs_large
            if any(any(ord(char) > 127 for char in tag) for tag in job["tags"])
        ]
        self.assertEqual(len(unicode_jobs), 5)

    def test_large_jobs_have_exact_empty_output_count(self) -> None:
        empty_output_jobs = [job for job in self.jobs_large if job["output_lines"] == []]
        self.assertEqual(len(empty_output_jobs), 5)

    def test_config_json_exists_and_valid(self) -> None:
        config_path = self.fixtures_dir / "config.json"
        self.assertTrue(config_path.exists())
        with config_path.open(encoding="utf-8") as handle:
            config = json.load(handle)
        self.assertIn("queue_name", config)

    def test_edge_cases_file_exists(self) -> None:
        edge_path = self.fixtures_dir / "fixtures-edge-cases.json"
        self.assertTrue(edge_path.exists())
        with edge_path.open(encoding="utf-8") as handle:
            edges = json.load(handle)
        self.assertGreaterEqual(len(edges), 5)

    def test_replay_module_files_exist(self) -> None:
        replay_dir = self.fixtures_dir / "replay"
        self.assertTrue((replay_dir / "stream.py").exists())
        self.assertTrue((replay_dir / "stream.go").exists())
        self.assertTrue((replay_dir / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
