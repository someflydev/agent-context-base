# TaskFlow Monitor - Python (Typer + Textual)

Canonical Python dual-mode terminal example. It monitors a fixture-backed job
queue with a Typer CLI surface and a Textual dashboard for interactive
inspection.

## Stack

- CLI: Typer
- TUI: Textual
- Python 3.11+

## Usage

```bash
pip install -e .

taskflow list
taskflow list --status failed --output json
taskflow inspect job-001
taskflow stats
taskflow watch
taskflow watch --no-tui
```

## Architecture

- `taskflow/core/`: domain logic for loading, filtering, and stats
- `taskflow/cli/`: Typer commands and output formatting
- `taskflow/tui/`: Textual dashboard widgets and app wiring
- `tests/smoke/`: fixture-backed CLI smoke tests that do not need a TTY

## Testing

```bash
pytest tests/smoke/
pytest tests/unit/
```

## Validation Approach

Use `taskflow watch --no-tui` for CI smoke coverage. Full-screen Textual
interaction is currently validated manually per
`docs/terminal-validation-contract.md`; PTY automation is a Phase 2 follow-up.

## When to Use This Stack

Use Typer + Textual for Python operator consoles that need a scriptable CLI and
a richer full-screen dashboard.
