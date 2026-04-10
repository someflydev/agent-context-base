# Add Terminal Canonical Example

Use this workflow when adding a new canonical terminal example (CLI, TUI, or
dual-mode) to `examples/canonical-terminal/`.

## Preconditions

- target language and stack chosen (see `context/router/stack-router.md`)
- archetype confirmed (`cli-tool` / `terminal-tui` / `terminal-dual-mode`)
- fixture corpus available at `examples/canonical-terminal/fixtures/`

## Sequence

1. Create `examples/canonical-terminal/<language-stack>/` with:
   - `core/` - domain logic (no I/O, no terminal APIs)
   - `cli/` - CLI entry surface
   - `tui/` - TUI entry surface (if applicable)
   - `tests/` - smoke tests (non-interactive, fixture-backed)
   - `README.md` - purpose, usage, when to use this stack
2. Point tests at `examples/canonical-terminal/fixtures/` for all data.
3. Write at least one smoke test that:
   - runs without a TTY
   - loads fixture data
   - asserts on at least one marker or structured output field
4. Add manifest entry or update `examples/canonical-terminal/CATALOG.md`.
5. Confirm the stack is registered in `context/router/stack-router.md`.
6. Run smoke tests.

## Outputs

- working example in `examples/canonical-terminal/<language-stack>/`
- passing smoke test
- `CATALOG.md` entry

## Related Doctrine

- `context/doctrine/terminal-ux-first-class.md` (ALL 11 rules)
- `context/doctrine/smoke-test-philosophy.md`

## Common Pitfalls

- domain logic duplicated in CLI and TUI layers
- smoke test that requires a live TTY or network
- no `README.md` or `CATALOG.md` entry
- TUI that has no non-interactive fallback
