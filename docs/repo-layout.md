# Repo Layout

The repository is organized so assistants can route first, compose or generate `.acb/` payloads, and verify that the system still matches its own documentation.

| Path | Role |
| --- | --- |
| [`README.md`](../README.md) | Front door for humans and assistants. |
| [`AGENT.md`](../AGENT.md), [`CLAUDE.md`](../CLAUDE.md) | Minimal assistant boot docs. |
| [`context/specs/`](../context/specs/README.md) | Canonical product, architecture, agent, and evolution modules. |
| [`context/validation/`](../context/validation/README.md) | Canonical validation modules. |
| [`context/acb/`](../context/acb/README.md) | Payload composition rules. |
| `context/router/`, `context/doctrine/`, `context/workflows/`, `context/stacks/`, `context/archetypes/`, `context/anchors/`, `context/skills/` | Broader routing and support guidance used by manifests and startup flows, including terminal capability routing. |
| [`manifests/`](../manifests) | Machine-readable context bundles and generation defaults. |
| [`examples/`](../examples/README.md) | Canonical examples, including terminal tooling under `examples/canonical-terminal/`. |
| [`templates/`](../templates/README.md) | Bootstrap scaffolds. |
| [`scripts/`](../scripts/README.md) | Generation, composition, inspection, and verification tools. |
| [`verification/`](../verification/README.md) | Verification suites and fixtures. |

## Terminal Tooling Additions

| Path | Role |
| --- | --- |
| `examples/canonical-terminal/` | Terminal tool examples: CLI, TUI, dual-mode across 7 languages. See `examples/canonical-terminal/CATALOG.md` for the cross-language index. |
| `context/archetypes/terminal-tui.md` | Archetype guidance for full-screen terminal UIs. |
| `context/archetypes/terminal-dual-mode.md` | Archetype guidance for shared CLI + TUI tools. |
| `context/doctrine/terminal-ux-first-class.md` | Terminal UX doctrine and rules for examples. |
| `context/stacks/terminal-*.yaml` | 14 stack definitions for terminal tooling across Python, Rust, Go, TypeScript, Java, Ruby, and Elixir. |
| `context/workflows/add-terminal-example.md` | Workflow for adding a new canonical terminal example. |
