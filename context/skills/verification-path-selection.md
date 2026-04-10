# Verification Path Selection

Use this skill to determine which verification level a given change surface requires.

## Procedure

1. identify the primary change surface
2. apply the decision tree:
   - **storage write or read** → real integration test against `docker-compose.test.yml`
     → load `context/workflows/add-storage-integration.md`
   - **UI state or HTMX fragment** → Playwright e2e test against the running app
     → load `context/workflows/add-playwright-ui-verification.md`
   - **pure logic, transforms, parsing** → unit test, no docker needed
   - **boot health, happy path** → smoke test, can run without full infra
     → load `context/workflows/add-smoke-tests.md`
   - **terminal output (CLI, TUI, or dual-mode)** → terminal validation path
     → load `context/skills/terminal-validation-path-selection.md`
3. when the change surface spans two types (e.g., storage write plus a new route), load the workflow for each surface
4. escalation rule: when in doubt between two levels, use the higher-confidence level
5. verification is not complete until a test, harness, or check was actually run — generation alone is not verification

## Good Triggers

- "which test level applies here"
- "should this be a smoke test or integration test"
- "what verification does this change need"
- "is a unit test sufficient"
- "which workflow for testing this"
- "which test level for a terminal tool"
- "do I need a PTY test or a smoke test"

## Avoid

- calling a mock-backed test an integration test
- claiming a smoke test covers a storage boundary
- skipping verification because "the logic is simple"
- treating plausible generation as equivalent to a passing test run

## See Also

- `terminal-validation-path-selection.md` — full decision tree for terminal changes
