# Terminal Canonical Example Catalog

All examples implement the TaskFlow Monitor domain: a fixture-backed job queue
inspector with CLI and TUI surfaces.

Fixture corpus: `examples/canonical-terminal/fixtures/`
Domain: jobs with `id`, `name`, `status`, `started_at`, `duration_s`, `tags`,
`output_lines`

---

## Python

### python-typer-textual/ - Flagship
- Stack: Typer (CLI) + Textual (TUI)
- Mode: Dual-mode (CLI + full-screen TUI)
- Install: `pip install -e .`
- Smoke: `pytest tests/smoke/`
- When to use: Python operator consoles, dual-mode tools, interactive dashboards

### python-click-blessed/ - Secondary
- Stack: Click (CLI) + Blessed (terminal interaction)
- Mode: CLI + lightweight interactive pager
- Install: `pip install -e .`
- Smoke: `pytest tests/smoke/`
- When to use: Lighter Python CLIs, colored output, simple key navigation

---

## Rust

### rust-clap-ratatui/ - Flagship
- Stack: clap (CLI) + ratatui + crossterm (TUI)
- Mode: Dual-mode
- Build: `cargo build --release`
- Smoke: `cargo test`
- When to use: High-performance Rust tools, operator dashboards, queue monitors

### rust-argh-tui-realm/ - Secondary
- Stack: argh (CLI) + tui-realm (component TUI)
- Mode: Dual-mode
- Build: `cargo build --release`
- Smoke: `cargo test`
- When to use: Rust tools where CLI is simple and TUI benefits from component model

---

## Go

### go-cobra-bubbletea/ - Flagship
- Stack: Cobra (CLI) + Bubble Tea + lipgloss (TUI)
- Mode: Dual-mode
- Build: `go build`
- Smoke: `go test ./tests/...`
- When to use: Go tools with multi-command tree + functional TUI model

### go-urfave-tview/ - Secondary
- Stack: urfave/cli + tview (TUI)
- Mode: Dual-mode
- Build: `go build`
- Smoke: `go test ./tests/...`
- When to use: Simpler Go CLIs where widget primitives matter more than
  message-driven purity

---

## TypeScript

### typescript-commander-ink/ - Flagship
- Stack: Commander (CLI) + Ink + React (TUI)
- Mode: Dual-mode
- Install: `npm install && npm run build`
- Smoke: `npm test`
- When to use: TypeScript/Node devtools with React component TUI

### typescript-yargs-blessed/ - Secondary
- Stack: Yargs (CLI) + Blessed (TUI)
- Mode: CLI + ncurses-style TUI
- Install: `npm install && npm run build`
- Smoke: `npm test`
- When to use: TypeScript CLIs with classic ncurses-style widgets; no React

---

## Java

### java-picocli-lanterna/ - Flagship
- Stack: picocli (CLI) + Lanterna (TUI)
- Mode: Dual-mode
- Build: `mvn package`
- Smoke: `mvn test`
- When to use: JVM services, enterprise Java, operator consoles on JVM

### java-jcommander-jline/ - Secondary
- Stack: JCommander (CLI) + JLine 3 (interactive shell)
- Mode: CLI + REPL shell
- Build: `mvn package`
- Smoke: `mvn test`
- When to use: Java tools needing readline UX, tab completion, command history;
  not a full-screen TUI

---

## Ruby

### ruby-thor-tty/ - Flagship
- Stack: Thor (CLI) + TTY::Prompt + TTY::Table
- Mode: Guided interactive CLI (prompt-driven, not full-screen TUI)
- Install: `bundle install`
- Smoke: `bundle exec ruby tests/smoke/test_cli_smoke.rb`
- When to use: Ruby operator workflows, guided remediations, wizards

### ruby-clamp-tty/ - Secondary
- Stack: Clamp (CLI) + TTY::Reader
- Mode: CLI + raw keystroke pager
- Install: `bundle install`
- Smoke: `bundle exec ruby tests/smoke/test_cli_smoke.rb`
- When to use: Lighter Ruby CLIs with custom key-driven interaction

---

## Elixir

### elixir-optimus-ratatouille/ - Flagship
- Stack: Optimus (CLI) + Ratatouille (TUI) + GenServer
- Mode: Dual-mode + BEAM supervision
- Build: `mix escript.build`
- Smoke: `mix test`
- When to use: Elixir shops needing terminal operator console with OTP strengths

### elixir-optionparser-owl/ - Secondary
- Stack: OptionParser (built-in) + Owl
- Mode: CLI + rich terminal output
- Build: `mix escript.build (or mix run)`
- Smoke: `mix test`
- When to use: Mix tasks, simple Elixir scripts, rich CLI output without full TUI

---

## Quick Reference: Run All Smoke Tests

```bash
# Python
cd examples/canonical-terminal/python-typer-textual && pytest tests/smoke/
cd examples/canonical-terminal/python-click-blessed  && pytest tests/smoke/

# Rust
cd examples/canonical-terminal/rust-clap-ratatui    && cargo test
cd examples/canonical-terminal/rust-argh-tui-realm  && cargo test

# Go
cd examples/canonical-terminal/go-cobra-bubbletea   && go test ./tests/...
cd examples/canonical-terminal/go-urfave-tview      && go test ./tests/...

# TypeScript
cd examples/canonical-terminal/typescript-commander-ink  && npm test
cd examples/canonical-terminal/typescript-yargs-blessed  && npm test

# Java
cd examples/canonical-terminal/java-picocli-lanterna  && mvn test -q
cd examples/canonical-terminal/java-jcommander-jline  && mvn test -q

# Ruby
cd examples/canonical-terminal/ruby-thor-tty   && bundle exec ruby tests/smoke/test_cli_smoke.rb
cd examples/canonical-terminal/ruby-clamp-tty  && bundle exec ruby tests/smoke/test_cli_smoke.rb

# Elixir
cd examples/canonical-terminal/elixir-optimus-ratatouille && mix test
cd examples/canonical-terminal/elixir-optionparser-owl    && mix test
```
