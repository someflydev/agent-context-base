from __future__ import annotations

import unittest

from verification.helpers import REPO_ROOT, load_yaml_like


class AliasCatalogTests(unittest.TestCase):
    def test_alias_catalog_targets_exist_and_aliases_are_unique(self) -> None:
        path = REPO_ROOT / "context/router/alias-catalog.yaml"
        data = load_yaml_like(path)
        self.assertEqual(data.get("version"), 2)

        for section in ("tasks", "stacks", "archetypes", "capabilities"):
            entries = data.get(section)
            self.assertIsInstance(entries, list)
            seen: set[str] = set()
            for entry in entries:
                self.assertIsInstance(entry, dict)
                alias = str(entry.get("alias", "")).strip()
                raw_target = entry.get("target", "")
                targets = raw_target if isinstance(raw_target, list) else [str(raw_target).strip()]
                with self.subTest(section=section, alias=alias):
                    self.assertTrue(alias)
                    self.assertNotIn(alias, seen)
                    for t in targets:
                        with self.subTest(target=t):
                            self.assertTrue((REPO_ROOT / str(t)).exists(), str(t))
                seen.add(alias)


if __name__ == "__main__":
    unittest.main()
