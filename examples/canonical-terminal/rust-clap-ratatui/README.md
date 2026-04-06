# TaskFlow Monitor - Rust (clap + ratatui)

Flagship Rust dual-mode terminal example. Demonstrates clap-based CLI parsing
with a ratatui terminal dashboard sharing a pure domain core.

## Stack

- CLI: clap
- TUI: ratatui + crossterm

## Usage

```bash
cargo build --release
./target/release/taskflow list
./target/release/taskflow list --status failed --output json
./target/release/taskflow watch --no-tui
./target/release/taskflow watch
```

## Testing

```bash
cargo test
```

## Architecture

- `src/core/`: domain logic for loading, filtering, and stats
- `src/cli/`: command execution and output formatting
- `src/tui/`: ratatui application state and rendering

## When to Use

High-performance Rust tools needing both a scriptable CLI and a rich terminal
UI.

