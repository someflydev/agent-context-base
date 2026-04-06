# Terminal TUI

Use this archetype for full-screen terminal user interface applications driven
by keyboard input, with panels, tables, detail views, and event loops.

## Common Goals

- full-screen dashboard or inspector UI
- keyboard navigation and command shortcuts
- live or fixture-backed data display
- clean exit and signal handling

## Required Doctrine

- `context/doctrine/terminal-ux-first-class.md`
- `context/doctrine/testing-philosophy.md`
- `context/doctrine/smoke-test-philosophy.md`

## Required Patterns

- non-interactive mode with `--no-tui` or `--output json` (mandatory)
- PTY-based or scripted TUI validation path
- shared domain core (separate from rendering layer)
- fixture-backed canonical path

## Routing

When asked to build a TUI dashboard, monitoring console, or interactive
inspector, prefer this archetype over `cli-tool`.

## Language Stack Options

See `context/router/stack-router.md` -> terminal stacks section.

## Canonical Examples

- `examples/canonical-terminal/python-typer-textual/`
- `examples/canonical-terminal/rust-clap-ratatui/`
- `examples/canonical-terminal/go-cobra-bubbletea/`
- `examples/canonical-terminal/typescript-commander-ink/`
- `examples/canonical-terminal/java-picocli-lanterna/`
- `examples/canonical-terminal/elixir-optimus-ratatouille/`

## Validation Path

- `python scripts/run_verification.py --tier fast`
- smoke tests in each example's `tests/` directory
- PTY harness guidance in `docs/terminal-validation-contract.md` (PROMPT_101)

## Common Pitfalls

- no non-interactive fallback
- TTY-dependent smoke tests (breaks CI)
- domain logic embedded in TUI event handlers instead of shared core
- no keyboard shortcut reference in `--help` output
