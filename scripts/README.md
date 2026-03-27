# Scripts

This directory contains lightweight tooling for generation, `.acb/` composition, inspection, and verification.

## Primary Commands

- `python scripts/new_repo.py ...`
  Generates a descendant repo with `.acb/`, prompts, startup docs, and optional starter assets.
- `python scripts/acb_payload.py ...`
  Composes `.acb/specs/*.md`, validation artifacts, coverage summaries, and `.acb/INDEX.json`.
- `python scripts/validate_context.py`
  Verifies repo integrity and generated-repo assumptions.
- `python scripts/run_verification.py --tier fast`
  Runs the fast verification baseline.
- `python scripts/preview_context_bundle.py <manifest> --show-weights --show-anchors`
  Shows what context would load first.

## Repo-Local `.acb` Tools

These are now vendored into generated repos under `.acb/scripts/`:

- `acb_inspect.py`
- `acb_verify.py`

Use them to inspect selected source modules, view coverage, and detect payload or canonical drift.
