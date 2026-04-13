from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestFakerArcFoundation(unittest.TestCase):
    def test_doctrine_exists(self) -> None:
        path = REPO_ROOT / "context/doctrine/synthetic-data-realism.md"
        self.assertTrue(path.exists())
        text = path.read_text()
        for rule in range(1, 8):
            self.assertIn(f"Rule {rule}", text)

    def test_archetype_exists(self) -> None:
        path = REPO_ROOT / "context/archetypes/synthetic-data-generator.md"
        self.assertTrue(path.exists())
        text = path.read_text()
        self.assertIn("context/doctrine/synthetic-data-realism.md", text)
        self.assertIn("context/skills/synthetic-dataset-design.md", text)

    def test_all_ten_stacks_exist(self) -> None:
        stack_paths = [
            "context/stacks/faker-python.yaml",
            "context/stacks/faker-javascript.yaml",
            "context/stacks/faker-go.yaml",
            "context/stacks/faker-rust.yaml",
            "context/stacks/faker-java.yaml",
            "context/stacks/faker-kotlin.yaml",
            "context/stacks/faker-scala.yaml",
            "context/stacks/faker-ruby.yaml",
            "context/stacks/faker-php.yaml",
            "context/stacks/faker-elixir.yaml",
        ]
        for relative_path in stack_paths:
            self.assertTrue((REPO_ROOT / relative_path).exists(), relative_path)

    def test_skills_exist(self) -> None:
        library_path = REPO_ROOT / "context/skills/faker-library-selection.md"
        design_path = REPO_ROOT / "context/skills/synthetic-dataset-design.md"
        self.assertTrue(library_path.exists())
        self.assertTrue(design_path.exists())
        text = design_path.read_text()
        for step in range(1, 8):
            self.assertIn(f"Step {step}", text)

    def test_workflow_exists(self) -> None:
        path = REPO_ROOT / "context/workflows/add-faker-example.md"
        self.assertTrue(path.exists())
        self.assertIn(
            "context/doctrine/synthetic-data-realism.md",
            path.read_text(),
        )

    def test_manifest_exists(self) -> None:
        path = REPO_ROOT / "manifests/faker-polyglot.yaml"
        self.assertTrue(path.exists())
        self.assertIn("faker-python", path.read_text())

    def test_router_updated_task(self) -> None:
        text = (REPO_ROOT / "context/router/task-router.md").read_text()
        self.assertIn("synthetic-data-realism", text)
        self.assertIn("faker-library-selection", text)

    def test_router_updated_archetype(self) -> None:
        text = (REPO_ROOT / "context/router/archetype-router.md").read_text()
        self.assertIn("synthetic-data-generator", text)


if __name__ == "__main__":
    unittest.main()
