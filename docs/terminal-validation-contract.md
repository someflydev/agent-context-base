# Terminal Validation Contract

## Purpose

Defines how terminal tools (CLI, TUI, dual-mode) must be tested to satisfy the
terminal tooling doctrine in
`context/doctrine/terminal-ux-first-class.md`.

## 1. CLI Smoke Tests

Every terminal example must include at least one CLI smoke test that:

- invokes the tool in non-interactive (headless) mode
- loads fixture data from `examples/canonical-terminal/fixtures/`
- asserts on at least one marker or structured output field
- passes without a TTY such as `TERM=dumb` or redirected stdout
- runs in under 5 seconds

Assertion strategies:

- marker-based: output contains `BEGIN_TABLE` / `END_TABLE`,
  `BEGIN_JOB` / `END_JOB`, or equivalent
- structured output: use `--output json` and assert on parsed fields
- exit-code: assert `0` for success and non-zero for error paths

Preferred assertion: `--output json` plus parsed field assertions. Fallback:
consistent human-readable markers.

## 2. CLI Integration Tests

When a terminal example supports a live backend such as a real database or API,
integration tests may target that backend. Integration tests:

- live in `tests/integration/`
- are not required to pass without a live backend
- are not included in `--tier fast` verification runs
- must be gated and skipped when the backend is unavailable

## 3. TUI Validation

TUI applications must have a documented validation path. Preferred options:

### Option A: PTY plus pexpect

Use `pexpect` or an equivalent PTY harness to spawn the TUI, send keystrokes,
capture rendered output, assert on text patterns, and confirm the app exits
cleanly on `q`.

### Option B: Headless `--no-tui`

The tool accepts `--no-tui` or equivalent to run the same domain flow and print
fixture-backed results to stdout without entering TUI mode. This is the
mandatory CI smoke path.

### Option C: Scripted transcript

Provide a documented manual script describing how to launch the tool, which
keys to press, what screens should appear, and where automation is still
missing.

Every TUI tool must support Option B even when Option A is also implemented.

## 4. Output Assertion Markers

CLI tools in this repo use marker-based sections when human-readable output is
selected. Markers make output assertable without parsing ANSI formatting.

Standard markers:

- `<!-- BEGIN_JOBS -->` / `<!-- END_JOBS -->`
- `<!-- BEGIN_JOB_DETAIL -->` / `<!-- END_JOB_DETAIL -->`
- `<!-- BEGIN_STATS -->` / `<!-- END_STATS -->`
- `<!-- BEGIN_ERROR -->` / `<!-- END_ERROR -->`

Alternative marker formats are acceptable when they fit the language surface,
for example:

- `## BEGIN_JOBS ##` / `## END_JOBS ##`
- `[BEGIN_JOBS]` / `[END_JOBS]`

Use one consistent marker scheme per example and document it in the example
README.

## 5. Fixture-First Rule

All smoke tests must load data from
`examples/canonical-terminal/fixtures/` and never from a live backend. Smoke
tests must work in:

- CI without a running service
- offline environments
- fresh clones without configuration

The shared fixture corpus includes:

- `jobs.json`: 20 job records with varied statuses, tags, and durations
- `events.json`: 30 event stream records for job state transitions
- `config.json`: sample tool configuration such as queue name and refresh
  interval

## 6. Language-Specific Notes

Python (`Typer` + `Textual`, `Click` + `Blessed`):

- `pytest` or `unittest` for CLI smoke tests
- `pexpect` for PTY-based TUI tests when feasible
- Textual test helpers for widget-level testing when useful

Rust (`clap` + `ratatui`, `argh` + `tui-realm`):

- `cargo test` for unit and integration tests
- `ratatui::backend::TestBackend` for draw-output unit tests
- required non-interactive `--no-tui` path

Go (`Cobra` + `Bubble Tea`, `urfave` + `tview`):

- `go test` for CLI tests
- Bubble Tea model tests for update and render behavior
- required non-interactive `--no-tui` path

TypeScript (`Commander` + `Ink`, `Yargs` + `Blessed`):

- `jest` or `vitest` for CLI tests
- `@ink-testing-library` for rendered component checks
- required non-interactive `--no-tui` path

Java (`picocli` + `Lanterna`, `JCommander` + `JLine`):

- `JUnit 5` plus `picocli CommandLine` for CLI tests
- `VirtualTerminal` or `MockTerminal` for TUI unit tests
- required non-interactive `--no-tui` path

Ruby (`Thor` + `TTY`, `Clamp` + `TTY`):

- `RSpec` or `minitest` for CLI tests
- `TTY::TestPrompt` for prompt-level headless testing
- required non-interactive `--no-tui` or `--batch` path

Elixir (`Optimus` + `Ratatouille`, `OptionParser` + `Owl`):

- `ExUnit` for all tests
- fake backends when the chosen TUI stack supports them
- required non-interactive `--no-tui` or test-mode override

## 7. Smoke Test Structure Convention

Canonical example smoke tests should be organized as:

```text
tests/
  smoke/
    test_cli_smoke.*   # non-interactive CLI invocations and output assertions
    test_tui_pty.*     # optional PTY-based TUI validation
  unit/
    test_core.*        # domain core unit tests
```

Language-specific naming variations are acceptable. `tests/smoke/test_cli_smoke.*`
is mandatory.

## 8. Verification Integration

Terminal smoke tests integrate with verification tiers as follows:

- `--tier fast`: runs smoke tests for implemented terminal examples and must
  pass without network or TTY
- `--tier medium` or `--tier heavy`: may run backend-dependent integration
  tests when backends are available
- `--tier terminal`: runs the shared cross-language terminal harness and may
  include PTY-driven validation when dependencies are available

Implementers for later prompts must ensure terminal smoke tests pass under
`python3 scripts/run_verification.py --tier fast` and register example-specific
discovery paths in `verification/` when those examples land.

## 9. Phase 2 Additions

Phase 2 adds a shared harness under `verification/terminal/` so terminal
examples can be validated through one Python entry point instead of language-
specific test runners.

### Cross-Language Smoke Harness

- `verification/terminal/harness.py` runs per-example smoke commands with a
  shared timeout, fixture environment, pass/fail contract, and optional golden
  transcript assertion.
- `verification/terminal/registry.py` defines the 14 canonical terminal
  examples and their availability checks so missing toolchains or build
  artifacts skip gracefully instead of failing the entire run.
- `python3 scripts/run_terminal_tests.py --all` is the operator-facing entry
  point.

### Transcript Normalization

`verification/terminal/transcript.py` normalizes timestamps, job identifiers,
durations, ANSI escape sequences, and trailing whitespace before comparing CLI
output to golden files stored in `verification/terminal/goldens/`.
When a golden is missing, the first passing run bootstraps it automatically;
use `--update-goldens` to intentionally refresh an existing golden.

### PTY Interaction Harness

`verification/terminal/pty_harness.py` provides a scripted PTY interaction
harness using `pexpect`. Use it to test TUI applications that support
keyboard-driven exit.

Standard TUI test pattern:

```python
from verification.terminal.pty_harness import scripted_tui_test, make_watch_script

result = scripted_tui_test(
    cmd=["taskflow", "watch"],
    script=make_watch_script(),
    env={"TASKFLOW_FIXTURES_PATH": "..."},
)
assert result is True
```

PTY tests require `pexpect`. The shared terminal harness is exposed through
`python3 scripts/run_verification.py --tier terminal` or the standalone
`python3 scripts/run_terminal_tests.py --all` wrapper.

## 10. Optional: Docker Live-Data Mode

A minimal fixture-backed HTTP API is available in
`examples/canonical-terminal/docker/` for exploring live-data modes. This is
not required for any smoke test and must remain optional.
