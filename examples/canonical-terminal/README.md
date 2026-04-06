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
