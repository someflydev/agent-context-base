---
acb_origin: canonical
acb_source_path: context/validation/archetypes/terminal-dual-mode.md
acb_role: validation
acb_archetypes: [terminal-dual-mode]
acb_version: 1
---

## Terminal Dual-Mode Validation

## Required Structure

- `core/` exists and contains shared domain logic
- `cli/` exists and contains the CLI entry surface
- `tui/` exists and contains the TUI entry surface
- `tests/smoke/` exists and contains at least one CLI smoke test
- `README.md` exists and documents purpose and stack

## Smoke Test Contract

- `tests/smoke/test_cli_smoke.*` passes with `--no-tui` or equivalent
- the smoke test loads fixtures from
  `examples/canonical-terminal/fixtures/`
- the smoke test asserts on at least one output marker or JSON field

## Doctrinal Compliance

- all 10 rules in `context/doctrine/terminal-ux-first-class.md` apply
- non-interactive mode must be available via `--no-tui`, `--output json`, or
  an equivalent headless path
