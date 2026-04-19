from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class TestDoctrineFiles(unittest.TestCase):
    DOCTRINES = [
        "context/doctrine/jwt-auth-request-context.md",
        "context/doctrine/rbac-permission-taxonomy.md",
        "context/doctrine/tenant-boundary-enforcement.md",
        "context/doctrine/route-metadata-registry.md",
        "context/doctrine/me-endpoint-discoverability.md",
    ]

    def test_doctrine_structure(self) -> None:
        for relative in self.DOCTRINES:
            path = REPO_ROOT / relative
            with self.subTest(path=relative):
                self.assertTrue(path.exists(), relative)
                text = path.read_text(encoding="utf-8")
                self.assertIn("## Rules", text)
                self.assertGreaterEqual(text.count("Rule "), 5)
                self.assertIn("## Anti-Patterns", text)


class TestArchetypeFile(unittest.TestCase):
    def test_archetype_exists_and_references_doctrines(self) -> None:
        path = REPO_ROOT / "context/archetypes/tenant-aware-backend-api.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("## Core Capabilities", text)
        self.assertIn("## Doctrines Activated", text)
        self.assertIn("jwt-auth-request-context.md", text)
        self.assertIn("rbac-permission-taxonomy.md", text)
        self.assertIn("tenant-boundary-enforcement.md", text)
        self.assertIn("route-metadata-registry.md", text)
        self.assertIn("me-endpoint-discoverability.md", text)


class TestStackFiles(unittest.TestCase):
    STACKS = [
        "context/stacks/python-fastapi-pyjwt-rbac.md",
        "context/stacks/typescript-hono-jose-rbac.md",
        "context/stacks/go-echo-golang-jwt-rbac.md",
        "context/stacks/rust-axum-jsonwebtoken-rbac.md",
        "context/stacks/java-spring-jjwt-rbac.md",
        "context/stacks/kotlin-http4k-jjwt-rbac.md",
        "context/stacks/ruby-hanami-ruby-jwt-rbac.md",
        "context/stacks/elixir-phoenix-joken-rbac.md",
    ]

    def test_stack_files_exist_and_have_required_sections(self) -> None:
        for relative in self.STACKS:
            path = REPO_ROOT / relative
            with self.subTest(path=relative):
                self.assertTrue(path.exists(), relative)
                text = path.read_text(encoding="utf-8")
                self.assertIn("## Preferred JWT Library", text)
                self.assertIn("## Auth Architecture", text)
                self.assertIn("examples/canonical-auth/", text)


class TestSkillFiles(unittest.TestCase):
    SKILLS = [
        "context/skills/jwt-middleware-implementation.md",
        "context/skills/permission-catalog-design.md",
        "context/skills/me-endpoint-design.md",
        "context/skills/route-metadata-annotation.md",
    ]

    def test_skill_files_exist(self) -> None:
        for relative in self.SKILLS:
            path = REPO_ROOT / relative
            with self.subTest(path=relative):
                self.assertTrue(path.exists(), relative)
                self.assertIn(
                    "## Anti-Patterns",
                    path.read_text(encoding="utf-8"),
                )


class TestWorkflowFiles(unittest.TestCase):
    def test_add_protected_endpoint_has_eight_steps(self) -> None:
        path = REPO_ROOT / "context/workflows/add-protected-endpoint.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        for step in range(1, 9):
            self.assertIn(f"{step}.", text)

    def test_add_tenant_aware_example_has_ten_steps(self) -> None:
        path = REPO_ROOT / "context/workflows/add-tenant-aware-canonical-example.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        for step in range(1, 11):
            self.assertIn(f"{step}.", text)


class TestManifest(unittest.TestCase):
    def test_manifest_exists_and_lists_languages(self) -> None:
        path = REPO_ROOT / "manifests/auth-jwt-rbac-polyglot.yaml"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        for language in (
            "Python",
            "TypeScript",
            "Go",
            "Rust",
            "Java",
            "Kotlin",
            "Ruby",
            "Elixir",
        ):
            self.assertIn(language, text)


if __name__ == "__main__":
    unittest.main()
