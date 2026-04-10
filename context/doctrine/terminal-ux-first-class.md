# Terminal UX as a First-Class Architecture Target

## Purpose

Terminal tooling deserves first-class architectural treatment because it often
serves operators, automation pipelines, on-call workflows, and latency-sensitive
inspection tasks where scriptability and keyboard-driven interaction matter as
much as service APIs or browser UIs.

## Core Rules

### 1. Shared Domain Core

CLI and TUI surfaces must wrap a shared application core, not duplicate logic.
The core handles data loading, filtering, and state. Surfaces handle rendering
only.

### 2. Non-Interactive Mode is Mandatory

Every tool with a TUI mode must also work in non-interactive (CLI/headless)
mode. Accept `--no-tui`, `--output json`, or equivalent. CI pipelines must not
require a TTY.

### 3. Fixture-First Validation

Baseline validation must not depend on live network or OS state. Use fixture
files for the canonical happy path. Live backends are optional extensions.

### 4. Output Assertion Discipline

CLI output must be assertable. Prefer marker-tagged sections such as
`BEGIN_TABLE` / `END_TABLE` or structured JSON for machine-readable output. TUI
output is asserted via normalized transcripts or PTY harness.

### 5. Smoke Test Requirement

Every terminal example must have at least one smoke test that:

- runs in non-interactive (CLI) mode
- loads fixtures, not live data
- asserts on at least one marker or structured output field
- passes without a TTY (usable in CI)

### 6. PTY Validation for TUI

TUI applications must have a documented path for scripted or PTY-based
interaction testing. If no PTY harness is available for a language, document
the manual validation approach and add a TODO for automation.

### 7. Shared Fixture Corpus

All terminal examples share a fixture corpus at
`examples/canonical-terminal/fixtures/`. This ensures cross-language
consistency and cross-example test transferability.

### 8. Stack Alignment

Each terminal example must declare its stack (language + CLI library + TUI
library) in the stack file and must be reachable from the stack-router.

### 9. Router Discoverability

Terminal archetypes, stacks, and examples must be discoverable through:

- `context/router/archetype-router.md`
- `context/router/stack-router.md`
- `context/router/alias-catalog.yaml`

### 10. Manifest Registration

Each canonical terminal example must have a manifest entry in `manifests/` or
be listed in the terminal catalog at `examples/canonical-terminal/CATALOG.md`.

### 11. Cross-Language Behavioral Consistency

When multiple language implementations of the same terminal domain exist in
`canonical-terminal/`, they must be behaviorally consistent:

- Same command + same fixtures -> same output structure
- Verify with: `python3 scripts/run_terminal_comparison.py`
- A mismatch indicates a domain implementation error, not a language
  difference

## Anti-Patterns

- TUI-only tool with no scriptable fallback
- live network calls in smoke tests
- duplicated domain logic across CLI and TUI layers
- output formats that are hard to assert on in CI
- missing stack declaration or router entry for a new terminal example
