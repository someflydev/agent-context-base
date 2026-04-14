import os
import unittest
import subprocess

class TestElixirFakerExample(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.join(os.path.dirname(__file__), "../../../examples/canonical-faker/elixir")

    def test_mix_exs_exists(self):
        mix_path = os.path.join(self.base_dir, "mix.exs")
        self.assertTrue(os.path.exists(mix_path))
        with open(mix_path) as f:
            content = f.read()
            self.assertIn("faker", content)
            self.assertIn("ex_machina", content)

    def test_pipeline_uses_enum_map(self):
        path = os.path.join(self.base_dir, "lib/tenant_core/pipeline.ex")
        with open(path) as f:
            self.assertIn("Enum.map", f.read())

    def test_rand_seed_called(self):
        path = os.path.join(self.base_dir, "lib/tenant_core/pipeline.ex")
        with open(path) as f:
            self.assertIn(":rand.seed", f.read())

    def test_ex_machina_limitation_documented(self):
        path = os.path.join(self.base_dir, "lib/tenant_core/ex_machina_pipeline.ex")
        with open(path) as f:
            self.assertIn("NOT", f.read())

    def test_mix_task_exists(self):
        path = os.path.join(self.base_dir, "lib/mix/tasks/generate.ex")
        self.assertTrue(os.path.exists(path))
        with open(path) as f:
            self.assertIn("use Mix.Task", f.read())

    def test_elixir_build_if_available(self):
        if subprocess.call(["which", "mix"], stdout=subprocess.DEVNULL) != 0:
            self.skipTest("mix not found")
        
        result = subprocess.run(["mix", "deps.get"], cwd=self.base_dir)
        self.assertEqual(result.returncode, 0)
        
        result = subprocess.run(["mix", "compile"], cwd=self.base_dir)
        self.assertEqual(result.returncode, 0)

    def test_elixir_smoke_if_available(self):
        if subprocess.call(["which", "mix"], stdout=subprocess.DEVNULL) != 0:
            self.skipTest("mix not found")
        
        result = subprocess.run(["mix", "test", "test/tenant_core/smoke_test.exs"], cwd=self.base_dir)
        self.assertEqual(result.returncode, 0)

if __name__ == "__main__":
    unittest.main()
