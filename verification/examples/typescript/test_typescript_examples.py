from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT


class TypeScriptExampleTests(unittest.TestCase):
    def test_hono_handler_example_keeps_route_shape(self) -> None:
        path = REPO_ROOT / "examples/canonical-api/typescript-hono-handler-example.ts"
        text = path.read_text(encoding="utf-8")
        self.assertIn("Hono", text)
        self.assertRegex(text, r"[A-Za-z]+Router\.(get|post)\(")

    def test_playwright_examples_keep_basic_assertion_shape(self) -> None:
        examples = (
            "examples/canonical-integration-tests/playwright-backend-filtering-example.spec.ts",
            "examples/canonical-integration-tests/playwright-filter-counts-example.spec.ts",
        )
        for relative in examples:
            with self.subTest(relative=relative):
                text = (REPO_ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("test(", text)
                self.assertIn("expect(", text)
