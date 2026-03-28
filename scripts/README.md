# Scripts

This directory contains lightweight tooling for repo-local runtime continuity, generation, `.acb/` composition, inspection, and verification.

## Primary Commands

- `python3 scripts/work.py resume`
  Summarizes repo-local runtime state, staleness signals, and the next useful reads for a fresh session.
- `python3 scripts/work.py checkpoint`
  Scaffolds missing runtime files and reports when `PLAN.md`, `context/TASK.md`, `context/SESSION.md`, or `context/MEMORY.md` likely need refresh.
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

- `work.py`
- `acb_inspect.py`
- `acb_verify.py`

Use them to recover session state, inspect selected source modules, view coverage, and detect payload or canonical drift.
