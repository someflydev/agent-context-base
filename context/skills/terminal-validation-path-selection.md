# Terminal Validation Path Selection

Use this skill to choose the correct validation path for terminal tooling changes.

## Procedure

1. identify the primary terminal change surface:
   - CLI output, flags, subcommands -> non-interactive smoke test plus marker assertion
   - TUI rendering, keyboard flow -> PTY harness
   - JSON output structure -> smoke test plus `--output json` assertion
   - cross-language consistency -> comparison harness
   - fixture corpus schema or count -> fixture validation tests
   - transcript normalization needs -> normalized transcript assertion, not raw terminal diff
   - dual-mode regression risk -> prove both the headless path and the interactive path
2. apply the decision tree:
   - **CLI smoke test** -> run in non-interactive mode with fixtures, assert at least one `## BEGIN_JOBS ##` / `## END_JOBS ##` marker or an `--output json` field, and require it to pass without a TTY
   - **marker assertion** -> assert markers are present and entry count matches the expected fixture result
   - **marker assertion** -> prefer fixture-stable counts over broad substring checks when the command returns a collection
   - **JSON output assertion** -> parse with `json.loads()`, assert top-level fields and count, and do not diff raw text
   - **JSON output assertion** -> prefer structural field checks such as item count, required keys, and expected identifiers
   - **PTY harness** -> use `verification/terminal/pty_harness.py`, script keystrokes, assert on normalized ANSI-stripped transcript, and run it after smoke coverage rather than instead of smoke coverage
   - **PTY harness** -> script realistic keys such as navigation, inspect, and quit, and confirm the app exits cleanly
   - **comparison harness** -> run `scripts/run_terminal_comparison.py` and assert count and field matches across implemented non-stub examples only
   - **comparison harness** -> treat mismatches as domain drift, not as acceptable language variance
3. escalation rule: a TUI change requires both a non-interactive smoke test and PTY validation; one is not a substitute for the other
4. when the fixture corpus changes, also run the fixture validation tests
5. if a CLI and TUI share a core path, choose the smoke test first to prove the shared headless path before asserting the interactive layer
6. verification is not complete until the selected test or harness was actually run
7. if the change touches more than one surface, keep the highest-confidence path for each surface instead of collapsing to one generic test

## Good Triggers

- "what test for this terminal change"
- "do I need a PTY test or a smoke test"
- "how do I validate TUI rendering"
- "is a smoke test enough for a new --output json flag"
- "which terminal verification path applies here"
- "how should I test a CLI output marker change"
- "how do I prove this tool works without a TTY"
- "which harness covers cross-language terminal parity"
- "what do I run after changing fixture counts"
- "should I assert the transcript or the JSON payload"
- "what validates a dual-mode terminal change"
- "how do I test a terminal tool after adding a new key flow"

## Avoid

- skipping the smoke test for TUI changes
- asserting on raw ANSI output instead of normalized transcripts
- treating JSON generation as equivalent to asserting the JSON structure
- running the comparison harness on stubs and reporting the result as a failure
- using PTY validation for a CLI-only change
- treating one passing PTY transcript as full coverage for CLI markers or JSON paths
- claiming verification is complete when the test plan was chosen but not run
- diffing a raw escape-sequence-heavy transcript when normalization is the documented path
- choosing the comparison harness as a substitute for example-level smoke coverage
- assuming manual terminal spot checks are equivalent to a recorded automated result

## Reference Files

- `docs/terminal-validation-contract.md`
- `verification/terminal/pty_harness.py`
- `verification/terminal/harness.py`
- `scripts/run_terminal_comparison.py`
- `context/doctrine/terminal-ux-first-class.md` (Rules 4, 5, 6)
