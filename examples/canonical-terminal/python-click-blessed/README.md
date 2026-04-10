# TaskFlow Monitor - Python (Click + Blessed)

Secondary Python terminal example demonstrating a lighter interactive approach
with Click for the CLI and Blessed for color and key handling.

## Stack

- CLI: Click
- Terminal UI: Blessed
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

## Testing

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Validation Approach

Use `taskflow watch --no-tui` for automated smoke coverage. The lightweight
interactive pager is still validated manually until a PTY harness is added.

## Architecture

- `taskflow/core.py`: shared fixture-backed domain logic
- `taskflow/cli.py`: Click command surface and output rendering
- `taskflow/watch.py`: lightweight Blessed-powered interactive watch mode

## Difference from Flagship

Typer + Textual provides a widget-based full-screen dashboard.
Click + Blessed keeps interaction line-oriented and lightweight.

## When to Use This Stack

Use this stack when a full dashboard is unnecessary and you mainly need
scriptable CLI commands plus a small amount of colored interactive navigation.
