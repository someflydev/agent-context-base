# Terminal Verification Harness

## Components

- `harness.py`: cross-language smoke test runner
- `registry.py`: example registry with build detection and skip logic
- `runner.py`: CLI entry point
- `transcript.py`: output normalization and golden comparison
- `goldens/`: golden transcript files; update with `--update-goldens`
- `pty_harness.py`: scripted PTY interaction harness for TUI validation
- `test_harness.py`: unittest coverage for harness configuration
- `test_pty_harness.py`: unittest coverage for PTY helpers

## Usage

```bash
# Run all available smoke tests
python3 scripts/run_terminal_tests.py --all

# Run specific example
python3 scripts/run_terminal_tests.py --example python-typer-textual

# Update golden transcripts
python3 scripts/run_terminal_tests.py --all --update-goldens

# Unittest for harness configuration
python3 -m unittest verification.terminal.test_harness -v
```

## Golden Strategy

On first run, golden files are created automatically for passing examples. On
subsequent runs, output is normalized and compared against the committed
goldens. `python3 scripts/run_verification.py --tier terminal` uses the same
bootstrap behavior. Use `--update-goldens` only when intentionally
regenerating existing goldens after output changes.

## Normalization

Non-deterministic values such as timestamps, job identifiers, durations, ANSI
escape sequences, and trailing whitespace are normalized before comparison.
