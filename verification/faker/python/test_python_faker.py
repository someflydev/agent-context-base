from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PYTHON_DIR = ROOT / "examples" / "canonical-faker" / "python"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


class TestPythonFakerExample(unittest.TestCase):
    def test_requirements_file_exists(self) -> None:
        path = PYTHON_DIR / "requirements.txt"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8").lower()
        self.assertIn("faker", text)
        self.assertIn("mimesis", text)
        self.assertIn("factory_boy", text)

    def test_generate_cli_exists(self) -> None:
        path = PYTHON_DIR / "generate.py"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("argparse", text)
        self.assertIn("--pipeline", text)
        self.assertIn("--profile", text)

    def test_faker_pipeline_importable(self) -> None:
        _load_module(PYTHON_DIR / "faker_pipeline" / "generators.py", "prompt121_faker_pipeline")

    def test_mimesis_pipeline_importable(self) -> None:
        _load_module(PYTHON_DIR / "mimesis_pipeline" / "generators.py", "prompt121_mimesis_pipeline")

    def test_factory_graph_importable(self) -> None:
        _load_module(PYTHON_DIR / "factory_graph" / "factories.py", "prompt121_factory_graph")

    def test_faker_smoke_profile_runs(self) -> None:
        try:
            import faker  # noqa: F401
        except ImportError:
            self.skipTest("faker is not installed")
        profiles = _load_module(PYTHON_DIR / "profiles.py", "prompt121_profiles_faker_runs")
        module = _load_module(PYTHON_DIR / "faker_pipeline" / "generators.py", "prompt121_faker_runs")
        with tempfile.TemporaryDirectory() as tmpdir:
            report = module.run_faker_pipeline(
                profile=profiles.Profile.SMOKE(),
                output_dir=Path(tmpdir),
            )
            self.assertTrue(report.ok)
            self.assertTrue((Path(tmpdir) / "organizations.jsonl").exists())
            self.assertTrue((Path(tmpdir) / "audit_events.jsonl").exists())

    def test_faker_smoke_reproducible(self) -> None:
        try:
            import faker  # noqa: F401
        except ImportError:
            self.skipTest("faker is not installed")
        profiles = _load_module(PYTHON_DIR / "profiles.py", "prompt121_profiles_faker_repro")
        module = _load_module(PYTHON_DIR / "faker_pipeline" / "generators.py", "prompt121_faker_repro")
        with tempfile.TemporaryDirectory() as left, tempfile.TemporaryDirectory() as right:
            module.run_faker_pipeline(profile=profiles.Profile.SMOKE(), output_dir=Path(left))
            module.run_faker_pipeline(profile=profiles.Profile.SMOKE(), output_dir=Path(right))
            left_text = (Path(left) / "organizations.jsonl").read_text(encoding="utf-8")
            right_text = (Path(right) / "organizations.jsonl").read_text(encoding="utf-8")
            self.assertEqual(left_text, right_text)

    def test_faker_validation_passes(self) -> None:
        try:
            import faker  # noqa: F401
        except ImportError:
            self.skipTest("faker is not installed")
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = [
                sys.executable,
                str(PYTHON_DIR / "generate.py"),
                "--pipeline",
                "faker",
                "--profile",
                "smoke",
                "--output-dir",
                tmpdir,
            ]
            run = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            validate = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "examples" / "canonical-faker" / "domain" / "validate_output.py"),
                    "--input-dir",
                    str(Path(tmpdir) / "smoke"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

    def test_mimesis_smoke_profile_runs(self) -> None:
        try:
            import mimesis  # noqa: F401
        except ImportError:
            self.skipTest("mimesis is not installed")
        profiles = _load_module(PYTHON_DIR / "profiles.py", "prompt121_profiles_mimesis")
        module = _load_module(PYTHON_DIR / "mimesis_pipeline" / "generators.py", "prompt121_mimesis_runs")
        with tempfile.TemporaryDirectory() as tmpdir:
            report = module.run_mimesis_pipeline(
                profile=profiles.Profile.SMOKE(),
                output_dir=Path(tmpdir),
            )
            self.assertTrue(report.ok)
            self.assertTrue((Path(tmpdir) / "organizations.jsonl").exists())
            self.assertTrue((Path(tmpdir) / "audit_events.jsonl").exists())

    def test_factory_graph_smoke_runs(self) -> None:
        try:
            import factory  # noqa: F401
        except ImportError:
            self.skipTest("factory_boy is not installed")
        profiles = _load_module(PYTHON_DIR / "profiles.py", "prompt121_profiles_factory")
        module = _load_module(PYTHON_DIR / "factory_graph" / "runner.py", "prompt121_factory_runner")
        with tempfile.TemporaryDirectory() as tmpdir:
            report = module.run_factory_graph(
                profile=profiles.Profile.SMOKE(),
                output_dir=Path(tmpdir),
            )
            self.assertTrue(report.ok)
            self.assertTrue((Path(tmpdir) / "organizations.jsonl").exists())
            self.assertTrue((Path(tmpdir) / "audit_events.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
