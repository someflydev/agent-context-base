# Terminal Dual-Mode (CLI + TUI)

Use this archetype for tools that expose a command-line interface for scripting
and automation, and a full-screen TUI for guided interactive use, both sharing
the same domain/application core.

## Common Goals

- identical business logic in CLI and TUI paths
- `--interactive` flag (or alias) to enter TUI mode from CLI
- machine-readable output in CLI mode (`--output json` / `--output table`)
- keyboard-driven inspection in TUI mode

## Required Doctrine

- `context/doctrine/terminal-ux-first-class.md` (ALL 10 rules apply here)
- `context/doctrine/testing-philosophy.md`
- `context/doctrine/smoke-test-philosophy.md`

## Structural Requirements

- `core/` directory: domain logic, data loading, filtering, state - no I/O
- `cli/` directory (or `cli.py` / `main.go` / etc.): CLI entry surface
- `tui/` directory (or `tui.py` / etc.): TUI entry surface
- Both surfaces import from `core/`. Neither surface reimplements domain logic.

## Routing

When asked to build an operator console, job monitor, queue inspector, or tool
that needs both scriptable and interactive modes, prefer this archetype.

## Language Stack Options (flagships)

- Python: Typer + Textual -> `examples/canonical-terminal/python-typer-textual/`
- Rust: clap + ratatui -> `examples/canonical-terminal/rust-clap-ratatui/`
- Go: Cobra + Bubble Tea -> `examples/canonical-terminal/go-cobra-bubbletea/`
- TypeScript: Commander + Ink -> `examples/canonical-terminal/typescript-commander-ink/`
- Java: picocli + Lanterna -> `examples/canonical-terminal/java-picocli-lanterna/`
- Ruby: Thor + TTY::Prompt -> `examples/canonical-terminal/ruby-thor-tty/`
- Elixir: Optimus + Ratatouille -> `examples/canonical-terminal/elixir-optimus-ratatouille/`

## Validation Path

- CLI smoke test (non-interactive, fixture-backed)
- TUI scripted test via PTY harness (language-dependent)
- `python scripts/run_verification.py --tier fast`

## Common Pitfalls

- core logic duplicated in both CLI and TUI paths
- TUI mode that cannot be headlessly exercised (no smoke path)
- `--interactive` flag missing from `--help`
- exit codes inconsistent between modes
