# TaskFlow Monitor - Go (Cobra + Bubble Tea)

Flagship Go dual-mode terminal example. Cobra handles the command tree and
Bubble Tea drives the interactive watch dashboard.

## Usage

```bash
go build -o taskflow ./...
./taskflow list
./taskflow list --status failed --output json
./taskflow watch --no-tui
./taskflow watch
```

## Testing

```bash
go test ./tests/...
```

## Validation Approach

Use `./taskflow watch --no-tui` for CI smoke coverage. Full-screen Bubble Tea
interaction is currently validated manually per
`docs/terminal-validation-contract.md`; PTY automation is a Phase 2 follow-up.

## Architecture

- `cmd/`: Cobra command definitions
- `internal/core/`: shared fixture-backed domain logic
- `internal/cli/`: marker-wrapped human output and JSON rendering
- `internal/tui/`: Bubble Tea model, update loop, and views

## When to Use

Choose this stack when you need a Go-native command tree with a full-screen TUI
that still degrades cleanly to non-interactive CLI output for smoke tests and
automation.
