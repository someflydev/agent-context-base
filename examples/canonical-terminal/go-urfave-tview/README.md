# TaskFlow Monitor - Go (urfave/cli + tview)

Secondary Go terminal example. It keeps the CLI smaller with `urfave/cli` and
uses `tview` widgets directly for the interactive dashboard.

## Usage

```bash
go build -o taskflow ./...
./taskflow list
./taskflow stats --output json
./taskflow watch --no-tui
./taskflow watch
```

## Testing

```bash
go test ./tests/...
```

## Validation Approach

Use `./taskflow watch --no-tui` for CI smoke coverage. The widget-driven tview
path is still validated manually until a PTY harness lands.

## When to Use vs Flagship

- Use Cobra + Bubble Tea for structured command trees and message-driven TUIs.
- Use urfave/cli + tview for simpler CLIs and direct high-level widgets.
