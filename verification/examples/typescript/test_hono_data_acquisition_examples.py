from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT, command_available, run_command


EXAMPLE_PATH = REPO_ROOT / "examples/canonical-data-acquisition/typescript-hono-source-sync-example.ts"
SHIMS_PATH = REPO_ROOT / "verification/examples/typescript/hono_bun_shims.d.ts"


class TypeScriptHonoDataAcquisitionExampleTests(unittest.TestCase):
    def test_hono_data_acquisition_example_contains_expected_sync_markers(self) -> None:
        text = EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("export interface SourceAdapter", text)
        self.assertIn("export async function archiveRawCapture", text)
        self.assertIn("async replayFromArchive", text)
        self.assertIn('syncRouter.post("/sources/github-releases/:owner/:repo/sync"', text)
        self.assertIn("await Bun.write(rawPath, fetchResult.body)", text)

    def test_hono_data_acquisition_example_is_tsc_checked_with_local_shims(self) -> None:
        if not command_available("tsc"):
            self.skipTest("TypeScript syntax checks require tsc on PATH")

        with tempfile.TemporaryDirectory() as temp_dir:
            tsconfig_path = Path(temp_dir) / "tsconfig.json"
            tsconfig_path.write_text(
                json.dumps(
                    {
                        "compilerOptions": {
                            "target": "ES2022",
                            "module": "ES2022",
                            "moduleResolution": "bundler",
                            "lib": ["ES2022", "DOM"],
                            "strict": True,
                            "noEmit": True,
                            "skipLibCheck": True,
                        },
                        "files": [SHIMS_PATH.as_posix(), EXAMPLE_PATH.as_posix()],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            result = run_command(["tsc", "--pretty", "false", "-p", tsconfig_path.as_posix()], timeout=120)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
