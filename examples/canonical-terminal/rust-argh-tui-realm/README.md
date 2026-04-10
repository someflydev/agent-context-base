# TaskFlow Monitor - Rust (argh + tui-realm)

Secondary Rust terminal example demonstrating a lighter CLI parser and a
component-driven terminal UI architecture.

## Stack

- CLI: argh
- TUI: tui-realm-style component model over ratatui

## Usage

```bash
cargo build --release
./target/release/taskflow list
./target/release/taskflow inspect job-001 --output json
./target/release/taskflow watch --no-tui
./target/release/taskflow watch
```

## Testing

```bash
cargo test
```

## Validation Approach

Use `taskflow watch --no-tui` for CI smoke coverage. The component-driven TUI
path is still validated manually until a PTY harness lands.

## Architecture

- `src/core.rs`: shared fixture-backed domain logic
- `src/cli.rs`: argh command parsing and output formatting
- `src/tui.rs`: tui-realm component tree and event loop

## When to Use vs Flagship

- Use clap + ratatui for richer subcommand ergonomics and direct control.
- Use argh + tui-realm when the CLI is simple and the TUI benefits from
  message-driven panels.
