from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT, run_command


PYTHON = sys.executable
WORK_SCRIPT = REPO_ROOT / "scripts" / "work.py"
CONTEXT_BUDGET_SCRIPT = REPO_ROOT / "scripts" / "context_budget.py"


def run_work_command(*args: str, cwd: Path) -> tuple[int, str, str]:
    script_path = cwd / "scripts" / "work.py"
    result = run_command([PYTHON, str(script_path), *args], cwd=cwd, timeout=240)
    return result.returncode, result.stdout, result.stderr


class WorkCommandTestCase(unittest.TestCase):
    def _run_checked_command(self, args: list[str], cwd: Path) -> str:
        result = run_command(args, cwd=cwd, timeout=240)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def _init_git_repo(self, repo: Path) -> None:
        self._run_checked_command(["git", "init"], cwd=repo)
        self._run_checked_command(["git", "config", "user.name", "ACB Test"], cwd=repo)
        self._run_checked_command(["git", "config", "user.email", "acb-test@example.com"], cwd=repo)

    def _write_file(self, repo: Path, relative_path: str, content: str) -> None:
        path = repo / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _scaffold_runtime_state(self, repo: Path) -> None:
        self._write_file(
            repo,
            "PLAN.md",
            "# PLAN.md\n\n## Active Phase\n- Verification hardening\n",
        )
        self._write_file(
            repo,
            "context/TASK.md",
            "# TASK.md\n\n## Current Slice\n- Add work.py command tests.\n",
        )
        self._write_file(
            repo,
            "context/SESSION.md",
            "# SESSION.md\n\n## Next Safe Step\n- Run work.py resume and verify its briefing output.\n",
        )
        self._write_file(
            repo,
            "context/MEMORY.md",
            "# MEMORY.md\n\n## Durable Rules\n- Keep runtime notes concise.\n",
        )

    def _create_repo(self) -> Path:
        temp_dir = tempfile.mkdtemp()
        repo = Path(temp_dir)
        self._init_git_repo(repo)
        self._write_file(repo, "scripts/work.py", WORK_SCRIPT.read_text(encoding="utf-8"))
        self._write_file(repo, "scripts/context_budget.py", CONTEXT_BUDGET_SCRIPT.read_text(encoding="utf-8"))
        self._write_file(repo, "README.md", "# Temp Repo\n")
        self._write_file(repo, ".prompts/PROMPT_95.txt", "Test prompt\n")
        self._scaffold_runtime_state(repo)
        return repo

    def _init_operator_console(self, repo: Path) -> None:
        code, _stdout, stderr = run_work_command("init-project", cwd=repo)
        self.assertEqual(code, 0, stderr)


class TestWorkStateJSON(WorkCommandTestCase):
    def test_init_project_creates_work_state_json(self) -> None:
        repo = self._create_repo()
        code, stdout, stderr = run_work_command("init-project", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertIn("Work Project Init:", stdout)
        work_state_path = repo / "work" / "projects" / repo.name / "WORK_STATE.json"
        self.assertTrue(work_state_path.exists())
        payload = json.loads(work_state_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["project_slug"], repo.name)
        self.assertEqual(payload["prompt_queue"], [])
        self.assertIn("validation_state", payload)

    def test_init_project_does_not_create_plan_under_work_project_dir(self) -> None:
        repo = self._create_repo()
        code, _stdout, stderr = run_work_command("init-project", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertFalse((repo / "work" / repo.name / "PLAN.md").exists())


class TestWorkCommands(WorkCommandTestCase):
    def test_verify_output_contains_expected_sections(self) -> None:
        repo = self._create_repo()
        self._init_operator_console(repo)
        code, stdout, stderr = run_work_command("verify", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertIn("Repo cleanliness:", stdout)
        self.assertIn("Commit discipline:", stdout)
        self.assertIn("Validation commands to run:", stdout)

    def test_status_reports_runtime_state_files(self) -> None:
        repo = self._create_repo()
        code, stdout, stderr = run_work_command("status", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertIn("Runtime State Status", stdout)
        self.assertIn("- PLAN.md: present", stdout)
        self.assertIn("- context/TASK.md: present", stdout)

    def test_checkpoint_reports_scaffold_actions_section(self) -> None:
        repo = self._create_repo()
        (repo / "context" / "SESSION.md").unlink()
        code, stdout, stderr = run_work_command("checkpoint", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertIn("Runtime Checkpoint", stdout)
        self.assertIn("Scaffold actions:", stdout)
        self.assertTrue((repo / "context" / "SESSION.md").exists())


class TestSessionContextBriefing(WorkCommandTestCase):
    def test_resume_output_contains_briefing_header(self) -> None:
        repo = self._create_repo()
        code, stdout, stderr = run_work_command("resume", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertIn("Session Context Briefing", stdout)

    def test_resume_briefing_sections_present(self) -> None:
        repo = self._create_repo()
        code, stdout, stderr = run_work_command("resume", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertIn("Runtime State:", stdout)
        self.assertIn("Memory Base:", stdout)
        self.assertIn("Complexity Budget:", stdout)
        self.assertIn("Recommended Next Action:", stdout)

    def test_resume_write_startup_log_creates_file(self) -> None:
        repo = self._create_repo()
        code, stdout, stderr = run_work_command("resume", "--write-startup-log", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertIn("Startup log:", stdout)
        logs_dir = repo / "logs" / "startup"
        self.assertTrue(logs_dir.exists())
        self.assertEqual(len(list(logs_dir.glob("*-resume.log"))), 1)

    def test_briefing_shows_last_trace(self) -> None:
        repo = self._create_repo()
        code, stdout, stderr = run_work_command(
            "startup-trace",
            "write",
            "--session",
            "trace briefing test",
            cwd=repo,
        )
        self.assertEqual(code, 0, stderr)
        code, stdout, stderr = run_work_command("resume", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertIn("Last Startup Trace:", stdout)
        self.assertIn("-trace.md", stdout)


class TestStartupTraceWrite(WorkCommandTestCase):
    def test_write_creates_file(self) -> None:
        repo = self._create_repo()
        code, stdout, stderr = run_work_command(
            "startup-trace",
            "write",
            "--session",
            "test trace",
            cwd=repo,
        )
        self.assertEqual(code, 0, stderr)
        self.assertIn("logs/startup/", stdout)
        self.assertEqual(len(list((repo / "logs" / "startup").glob("*-trace.md"))), 1)

    def test_write_output_contains_sections(self) -> None:
        repo = self._create_repo()
        code, _stdout, stderr = run_work_command(
            "startup-trace",
            "write",
            "--session",
            "test trace",
            "--files",
            "AGENT.md",
            "README.md",
            cwd=repo,
        )
        self.assertEqual(code, 0, stderr)
        trace_path = next((repo / "logs" / "startup").glob("*-trace.md"))
        text = trace_path.read_text(encoding="utf-8")
        self.assertIn("Startup Trace", text)
        self.assertIn("Declared Files Read", text)
        self.assertIn("Budget Estimate", text)
        self.assertIn("Router Decision", text)

    def test_write_with_files_scores_budget(self) -> None:
        repo = self._create_repo()
        code, _stdout, stderr = run_work_command(
            "startup-trace",
            "write",
            "--session",
            "budget trace",
            "--files",
            "AGENT.md",
            "context/TASK.md",
            "--primary-stack",
            "python-fastapi",
            "--archetype",
            "backend-api-service",
            cwd=repo,
        )
        self.assertEqual(code, 0, stderr)
        trace_path = next((repo / "logs" / "startup").glob("*-trace.md"))
        text = trace_path.read_text(encoding="utf-8")
        self.assertIn("Estimated Profile:", text)
        self.assertNotIn("Estimated Profile: unknown", text)

    def test_write_minimal_trace(self) -> None:
        repo = self._create_repo()
        code, _stdout, stderr = run_work_command(
            "startup-trace",
            "write",
            "--session",
            "minimal trace",
            cwd=repo,
        )
        self.assertEqual(code, 0, stderr)
        trace_path = next((repo / "logs" / "startup").glob("*-trace.md"))
        self.assertTrue(trace_path.exists())


class TestStartupTraceShow(WorkCommandTestCase):
    def test_show_no_files(self) -> None:
        repo = self._create_repo()
        code, stdout, stderr = run_work_command("startup-trace", "show", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertIn("No startup traces found", stdout)

    def test_show_after_write(self) -> None:
        repo = self._create_repo()
        code, _stdout, stderr = run_work_command(
            "startup-trace",
            "write",
            "--session",
            "show trace",
            cwd=repo,
        )
        self.assertEqual(code, 0, stderr)
        code, stdout, stderr = run_work_command("startup-trace", "show", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertIn("show trace", stdout)


class TestMemoryStructure(unittest.TestCase):
    def test_memory_index_exists(self) -> None:
        path = REPO_ROOT / "memory" / "INDEX.md"
        if not path.exists():
            self.skipTest("memory/INDEX.md is not present in this repo")
        self.assertTrue(path.read_text(encoding="utf-8").strip())

    def test_memory_tier_dirs_exist(self) -> None:
        memory_root = REPO_ROOT / "memory"
        if not memory_root.exists():
            self.skipTest("memory/ is not present in this repo")
        for name in ("concepts", "sessions", "summaries"):
            with self.subTest(name=name):
                self.assertTrue((memory_root / name).exists())

    def test_memory_tier_readmes_exist(self) -> None:
        memory_root = REPO_ROOT / "memory"
        if not memory_root.exists():
            self.skipTest("memory/ is not present in this repo")
        for name in ("concepts", "sessions", "summaries"):
            with self.subTest(name=name):
                self.assertTrue((memory_root / name / "README.md").exists())

    def test_memory_summaries_example_exists(self) -> None:
        summaries_dir = REPO_ROOT / "memory" / "summaries"
        if not summaries_dir.exists():
            self.skipTest("memory/summaries/ is not present in this repo")
        self.assertTrue(any(summaries_dir.glob("*.md")))


class TestWorkCompactionDoctrine(unittest.TestCase):
    def test_memory_compaction_discipline_exists(self) -> None:
        path = REPO_ROOT / "context" / "doctrine" / "memory-compaction-discipline.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("Compaction Defined", text)
        self.assertIn("3-Tier", text)
        self.assertIn("Triggers", text)

    def test_manage_work_queue_workflow_exists(self) -> None:
        path = REPO_ROOT / "context" / "workflows" / "manage-work-queue.md"
        self.assertTrue(path.exists())

    def test_checkpoint_and_resume_workflow_exists(self) -> None:
        path = REPO_ROOT / "context" / "workflows" / "checkpoint-and-resume.md"
        self.assertTrue(path.exists())

    def test_startup_context_visibility_doc_exists(self) -> None:
        path = REPO_ROOT / "docs" / "startup-context-visibility.md"
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
