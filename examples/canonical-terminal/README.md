# Terminal Canonical Examples

This directory contains canonical terminal tool examples across 7 languages.
Each example implements the TaskFlow Monitor domain: a job queue inspector with
CLI and TUI surfaces backed by fixture data.

## Domain

TaskFlow Monitor tracks jobs with: `id`, `name`, `status`
(`pending`/`running`/`done`/`failed`), `started_at`, `duration_s`, `tags`, and
`output_lines`.

Fixture data: `examples/canonical-terminal/fixtures/`

## Examples

Language examples are added by PROMPT_102-105. See `CATALOG.md` (PROMPT_106)
for the cross-language index and `DECISION_GUIDE.md` for stack selection
guidance.

## Implemented Examples

### Python

| Example | Stack | Mode |
|---------|-------|------|
| python-typer-textual/ | Typer + Textual | Dual-mode (CLI + TUI) |
| python-click-blessed/ | Click + Blessed | CLI + light interactive |

### Rust

| Example | Stack | Mode |
|---------|-------|------|
| rust-clap-ratatui/ | clap + ratatui | Dual-mode |
| rust-argh-tui-realm/ | argh + tui-realm | Dual-mode |

### Go

| Example | Stack | Mode |
|---------|-------|------|
| go-cobra-bubbletea/ | Cobra + Bubble Tea | Dual-mode |
| go-urfave-tview/ | urfave/cli + tview | Dual-mode |

### TypeScript

| Example | Stack | Mode |
|---------|-------|------|
| typescript-commander-ink/ | Commander + Ink | Dual-mode |
| typescript-yargs-blessed/ | Yargs + Blessed | CLI + classic TUI |

### Java

| Example | Stack | Mode |
|---------|-------|------|
| java-picocli-lanterna/ | picocli + Lanterna | Dual-mode |
| java-jcommander-jline/ | JCommander + JLine | CLI + REPL shell |

### Ruby

| Example | Stack | Mode |
|---------|-------|------|
| ruby-thor-tty/ | Thor + TTY::Prompt | Guided interactive CLI |
| ruby-clamp-tty/ | Clamp + TTY::Reader | CLI + raw key pager |

### Elixir

| Example | Stack | Mode |
|---------|-------|------|
| elixir-optimus-ratatouille/ | Optimus + Ratatouille | Dual-mode (GenServer-backed) |
| elixir-optionparser-owl/ | OptionParser + Owl | CLI + rich output |

## Running Python Examples

```bash
# Flagship
cd examples/canonical-terminal/python-typer-textual
pip install -e .
taskflow list
taskflow watch --no-tui

# Secondary
cd examples/canonical-terminal/python-click-blessed
pip install -e .
taskflow list
```

## Running Rust Examples

```bash
cd examples/canonical-terminal/rust-clap-ratatui && cargo test
cd examples/canonical-terminal/rust-argh-tui-realm && cargo test
```

## Running Go Examples

```bash
cd examples/canonical-terminal/go-cobra-bubbletea && GOCACHE=/tmp/go-build-cache GOPATH=/tmp/go-path go test ./tests/...
cd examples/canonical-terminal/go-urfave-tview && GOCACHE=/tmp/go-build-cache GOPATH=/tmp/go-path go test ./tests/...
```

## Running TypeScript Examples

```bash
cd examples/canonical-terminal/typescript-commander-ink && npm install && npm test
cd examples/canonical-terminal/typescript-yargs-blessed && npm install && npm test
```

## Running Java Examples

```bash
cd examples/canonical-terminal/java-picocli-lanterna && mvn test -q
cd examples/canonical-terminal/java-jcommander-jline && mvn test -q
```

## Running Ruby Examples

```bash
cd examples/canonical-terminal/ruby-thor-tty && bundle install && bundle exec ruby tests/smoke/test_cli_smoke.rb
cd examples/canonical-terminal/ruby-clamp-tty && bundle install && bundle exec ruby tests/smoke/test_cli_smoke.rb
```

## Running Elixir Examples

```bash
cd examples/canonical-terminal/elixir-optimus-ratatouille && mix deps.get && mix test
cd examples/canonical-terminal/elixir-optionparser-owl && mix deps.get && mix test
```

## Smoke Tests

```bash
# From each example directory, use the language-native fast test command:
pytest tests/smoke/
pytest tests/unit/
cargo test
go test ./tests/...
npm test
mvn test -q
bundle exec ruby tests/smoke/test_cli_smoke.rb
mix test
```

## Architecture

All examples share:

- a domain core (data loading, filtering, state) isolated from terminal I/O
- a CLI surface (subcommands, flags, `--output json/table`)
- optionally a TUI surface (`--interactive` mode or default for dual-mode tools)
- fixture-first smoke tests that pass without a TTY

## Related Docs

- `context/archetypes/terminal-dual-mode.md`
- `context/archetypes/terminal-tui.md`
- `context/doctrine/terminal-ux-first-class.md`
- `docs/terminal-validation-contract.md` (added by PROMPT_101)
