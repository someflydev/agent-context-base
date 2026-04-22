from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from work import GraftItem, build_graft_manifest, handle_graft  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]


def setup_minimal_repo_root(tmp_dir: Path) -> None:
    scripts_dir = tmp_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "work.py").write_text("# mock work.py for testing\n", encoding="utf-8")


class TestGraftManifest(unittest.TestCase):

    def test_graft_manifest_includes_work_py(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            manifest = build_graft_manifest(REPO_ROOT, target, no_prompts=False)
            dests = [item.dest for item in manifest]
            self.assertIn(Path("scripts/work.py"), dests)

    def test_graft_manifest_includes_memory_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            manifest = build_graft_manifest(REPO_ROOT, target, no_prompts=False)
            dests = [item.dest for item in manifest]
            self.assertIn(Path("memory/INDEX.md"), dests)

    def test_graft_manifest_excludes_prompts_when_flag_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            manifest = build_graft_manifest(REPO_ROOT, target, no_prompts=True)
            for item in manifest:
                self.assertFalse(
                    str(item.dest).startswith(".prompts/"),
                    f"Expected no .prompts/ item, found {item.dest}",
                )

    def test_graft_manifest_includes_prompts_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            manifest = build_graft_manifest(REPO_ROOT, target, no_prompts=False)
            dests = [item.dest for item in manifest]
            self.assertIn(Path(".prompts/analyze-and-reverse-engineer.txt"), dests)
            analyze_item = next(
                item for item in manifest
                if item.dest == Path(".prompts/analyze-and-reverse-engineer.txt")
            )
            self.assertIsNotNone(analyze_item.content)
            self.assertGreater(len(analyze_item.content), 0)

    def test_graft_manifest_work_py_content_matches_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            target.mkdir()
            manifest = build_graft_manifest(REPO_ROOT, target, no_prompts=True)
            work_py_item = next(item for item in manifest if item.dest == Path("scripts/work.py"))
            expected = (REPO_ROOT / "scripts" / "work.py").read_text(encoding="utf-8")
            self.assertEqual(work_py_item.content, expected)


class TestHandleGraftDryRun(unittest.TestCase):

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            setup_minimal_repo_root(repo_root)
            target = repo_root / "target_repo"
            target.mkdir()
            before = set(target.rglob("*"))
            handle_graft(repo_root, target=target, dry_run=True, force=False, no_prompts=True)
            after = set(target.rglob("*"))
            self.assertEqual(before, after)

    def test_dry_run_returns_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            setup_minimal_repo_root(repo_root)
            target = repo_root / "target_repo"
            target.mkdir()
            result = handle_graft(repo_root, target=target, dry_run=True, force=False, no_prompts=True)
            self.assertEqual(result, 0)

    def test_rejects_target_equal_to_repo_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            result = handle_graft(repo_root, target=repo_root, dry_run=False, force=False, no_prompts=True)
            self.assertEqual(result, 1)

    def test_rejects_nonexistent_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            nonexistent = repo_root / "does_not_exist"
            result = handle_graft(repo_root, target=nonexistent, dry_run=False, force=False, no_prompts=True)
            self.assertEqual(result, 1)


class TestHandleGraftExecution(unittest.TestCase):

    def test_writes_expected_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            setup_minimal_repo_root(repo_root)
            target = repo_root / "target_repo"
            target.mkdir()
            handle_graft(repo_root, target=target, dry_run=False, force=False, no_prompts=True)
            self.assertTrue((target / "scripts" / "work.py").exists())
            self.assertTrue((target / "memory" / "INDEX.md").exists())
            self.assertTrue((target / "CLAUDE.md").exists())
            self.assertTrue((target / "AGENT.md").exists())

    def test_force_flag_overwrites_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            setup_minimal_repo_root(repo_root)
            target = repo_root / "target_repo"
            target.mkdir()
            sentinel = "SENTINEL_CONTENT_DO_NOT_OVERWRITE"
            (target / "CLAUDE.md").write_text(sentinel, encoding="utf-8")
            handle_graft(repo_root, target=target, dry_run=False, force=True, no_prompts=True)
            content = (target / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertNotEqual(content, sentinel)

    def test_no_force_skips_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            setup_minimal_repo_root(repo_root)
            target = repo_root / "target_repo"
            target.mkdir()
            sentinel = "SENTINEL_CONTENT_DO_NOT_OVERWRITE"
            (target / "CLAUDE.md").write_text(sentinel, encoding="utf-8")
            handle_graft(repo_root, target=target, dry_run=False, force=False, no_prompts=True)
            content = (target / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertEqual(content, sentinel)


if __name__ == "__main__":
    unittest.main()
