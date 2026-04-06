# Concept: Verification Gate Overview

This repo uses three primary verification commands.

- `python3 -m unittest discover -s verification/unit -p "test_*.py" -v`
  Use for fast structural and script-focused unit coverage.
- `python3 scripts/validate_context.py`
  Use for repo integrity, manifests, prompt rules, and context consistency.
- `python3 scripts/run_verification.py --tier fast`
  Use for the standard local fast gate across the verification framework.

Tier guidance:

- `--tier fast` is the default completion gate for prompt-sized repo changes.
- Higher tiers add heavier checks and should be used when runtime surfaces changed.
- Run targeted example verification when a stack or canonical example changed.

Do not claim completion until the changed boundary has real proof, not doc updates alone.

_Last updated: 2026-04-05_
