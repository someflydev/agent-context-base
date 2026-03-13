from __future__ import annotations

import ast
import contextlib
import io
import unittest

from verification.helpers import REPO_ROOT, compat_dataclasses_module, load_python_module


EXAMPLE_PATH = REPO_ROOT / "examples/canonical-cli/python-cli-command-example.py"


def load_cli_module():
    return load_python_module(
        EXAMPLE_PATH,
        module_name="verification.examples.python.cli_example",
        stub_modules={"dataclasses": compat_dataclasses_module()},
    )


class CLIExampleTests(unittest.TestCase):
    def test_cli_example_parses(self) -> None:
        ast.parse(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_cli_json_output(self) -> None:
        module = load_cli_module()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            module.render_rows(module.load_rows(limit=2), output_format="json")
        text = output.getvalue()
        self.assertIn('"name": "daily-signups"', text)
        self.assertIn('"status": "ready"', text)

    def test_cli_table_output(self) -> None:
        module = load_cli_module()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            module.render_rows(module.load_rows(limit=2), output_format="table")
        text = output.getvalue()
        self.assertIn("name                status   owner", text)
        self.assertIn("daily-signups", text)


if __name__ == "__main__":
    unittest.main()
