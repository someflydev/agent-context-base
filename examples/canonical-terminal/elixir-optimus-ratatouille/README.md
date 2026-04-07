# TaskFlow Monitor - Elixir (Optimus + Ratatouille)

Flagship Elixir dual-mode terminal example. Optimus is used for the CLI entry
surface, Ratatouille provides a declarative TUI, and `Taskflow.JobStore`
demonstrates the BEAM state-holder pattern for a refreshable terminal app.

## Stack

- CLI: Optimus
- TUI: Ratatouille
- State model: GenServer
- Elixir 1.16+

## Usage

```bash
mix deps.get
mix escript.build
./taskflow list
./taskflow list --status failed --output json
./taskflow watch --no-tui
./taskflow watch
```

## Testing

```bash
mix test
```

## Validation Approach

Use `./taskflow watch --no-tui` for CI smoke coverage. Full-screen
Ratatouille interaction is currently validated manually per
`docs/terminal-validation-contract.md`; PTY automation is a Phase 2 follow-up.

## BEAM Architecture

`Taskflow.JobStore` is a GenServer that owns the current job list and supports a
refresh message. That makes the TUI refresh path honest to BEAM strengths
without forcing supervision into the simpler CLI-only flows.

## When to Use

Choose this stack when you want a real dual-mode terminal tool on the BEAM:
structured CLI parsing, a full-screen TUI, and supervised state that can grow
into live refresh or event-driven monitoring later.
