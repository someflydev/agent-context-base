# Repo Layout

The repository is organized so assistants can route first, load later, and avoid scanning broad directories by default.

| Path | Role |
| --- | --- |
| `README.md` | Front-facing overview and entrypoint for humans. |
| `AGENT.md`, `CLAUDE.md` | Minimal assistant boot docs. |
| `docs/` | Short orientation, architecture, and usage guides. |
| `context/doctrine/` | Durable rules: loading discipline, testing posture, prompt-first rules, deployment guardrails, and stop conditions. |
| `context/router/` | Task, stack, archetype, and alias routing logic. |
| `context/workflows/` | Task playbooks such as adding features, bootstrapping repos, or refining before commit. |
| `context/stacks/` | Framework and infra guidance for active implementation surfaces. |
| `context/archetypes/` | Repo-shape guidance such as backend service, CLI, local RAG, or prompt-first repo. |
| `context/anchors/` | Very small reminder docs for startup, isolation, and integrity work. |
| `context/memory/` | Rules and templates for `MEMORY.md`, stop hooks, and handoff snapshots. |
| `manifests/` | Machine-readable context bundles, triggers, repo signals, examples, and bootstrap defaults. |
| `examples/` | Canonical examples that should shape implementation after routing is narrow. |
| `templates/` | Generated-repo scaffolds. Useful for bootstrap, but lower authority than canonical examples. |
| `scripts/` | Bootstrap, preview, validation, repo-signal analysis, and continuity utilities. |
| `verification/` | Example registry, support matrix, tests, fixtures, and scenario harnesses. |

## Reading Order

1. `README.md`
2. `docs/context-boot-sequence.md`
3. `docs/repo-purpose.md`
4. `docs/repo-layout.md`
5. `docs/session-start.md`
6. one router, one workflow, one stack, and one example as needed

## Practical Rules

- Load doctrine only when the task activates a durable constraint.
- Load one workflow before mixing several.
- Load only the stacks on the active change surface.
- Prefer one canonical example over several near-matches.
- Treat templates as scaffolding, not proof of a canonical pattern.

## Extension Rule

When promoting a new stack or repo shape, keep the same pattern:

1. add or refine the router signals
2. add the focused stack or archetype guidance
3. add or update a manifest
4. add a canonical example only when the pattern is stable
5. add verification coverage so the example can stay trusted
