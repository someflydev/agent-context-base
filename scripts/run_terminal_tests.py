#!/usr/bin/env python3
"""Run the cross-language terminal verification harness."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from verification.terminal import runner  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(runner.main(sys.argv[1:]))
