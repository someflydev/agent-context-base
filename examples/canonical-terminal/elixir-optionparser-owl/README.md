# TaskFlow Monitor - Elixir (OptionParser + Owl)

Secondary Elixir example. It uses built-in `OptionParser` for command routing
and Owl for rich terminal output, styled tags, tables, and a simple refresh
loop without a full-screen TUI.

## Stack

- CLI: OptionParser
- Rich output: Owl
- Elixir 1.16+

## Usage

```bash
mix deps.get
mix escript.build
./taskflow_owl list
./taskflow_owl list --status failed --output json
./taskflow_owl watch --no-tui
./taskflow_owl watch --interval 2
```

## Testing

```bash
mix test
```

## Validation Approach

Use `./taskflow_owl watch --no-tui` for CI smoke coverage. Owl-based terminal
output stays scriptable, so PTY automation is optional rather than mandatory.

## Architecture

- `lib/taskflow/cli.ex`: OptionParser-driven command routing and output helpers
- `test/smoke/`: fixture-backed smoke coverage
- `test/unit/`: core filtering and stats assertions

## When to Use vs Flagship

- `Optimus + Ratatouille`: structured CLI + full-screen TUI + GenServer-backed refresh
- `OptionParser + Owl`: simpler CLIs and operator tools that need better output
  without a dashboard framework
