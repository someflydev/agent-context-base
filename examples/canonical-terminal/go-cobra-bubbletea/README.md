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

## Architecture

- `cmd/`: Cobra command definitions
- `internal/core/`: shared fixture-backed domain logic
- `internal/cli/`: marker-wrapped human output and JSON rendering
- `internal/tui/`: Bubble Tea model, update loop, and views

