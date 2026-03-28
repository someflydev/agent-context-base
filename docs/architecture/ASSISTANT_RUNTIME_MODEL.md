# Assistant Runtime Model

`agent-context-base` is a runtime for AI-assisted development. It turns a user request into a bounded context bundle, a preferred implementation pattern, a verification path, and a visible repo-local continuity checkpoint.

## Core Pipeline

1. Interpret the task.
2. Rehydrate repo-local runtime state with `scripts/work.py resume`.
3. Inspect narrow repo signals.
4. Route to one workflow, stack surface, and archetype.
5. Select the best-fit manifest.
6. Load the smallest justified context bundle.
7. Prefer one canonical example.
8. Implement in a reviewable slice.
9. Run `scripts/work.py checkpoint`.
10. Verify the changed boundary.

## Architectural Subsystems

| Subsystem | Role |
| --- | --- |
| Entry surface | `AGENT.md`, `CLAUDE.md`, generated profiles, and any maintained front docs define how assistants should start. |
| Router layer | `context/router/` maps natural language and repo signals onto workflows, stacks, archetypes, and aliases. |
| Context layer | `context/doctrine/`, `context/workflows/`, `context/stacks/`, and `context/archetypes/` hold durable guidance with clear authority boundaries. |
| Manifest layer | `manifests/` binds routing signals to required context, optional context, preferred examples, templates, warnings, and bootstrap defaults. |
| Example layer | `examples/` and `examples/catalog.json` provide canonical implementation patterns and ranking metadata. |
| Generation layer | `scripts/new_repo.py` and `templates/` create derived repos with generated profiles, boot docs, and optional Compose, prompt, seed, smoke, and integration assets. |
| Verification layer | `verification/`, `scripts/validate_context.py`, and `scripts/run_verification.py` keep manifests, examples, scripts, and generated repo shapes aligned. |
| Continuity layer | `scripts/work.py`, `PLAN.md`, `context/TASK.md`, `context/SESSION.md`, `context/MEMORY.md`, and handoff snapshots preserve current working state across sessions. |

## Source-of-Truth Order

1. Code, tests, and runnable examples define implementation reality.
2. Doctrine defines stable operating rules.
3. Manifests define the intended context bundle.
4. Canonical examples define the preferred implementation shape.
5. Templates provide scaffolding only.
6. `PLAN.md`, `context/TASK.md`, `context/SESSION.md`, `context/MEMORY.md`, and handoff snapshots preserve operational state, not policy.

## Why The Model Stays Narrow

The repo assumes large context is usually harmful. Reliability comes from:

- one dominant workflow instead of several adjacent playbooks
- one active stack surface instead of cross-stack blending
- one manifest instead of merged near-matches
- one canonical example instead of a hybrid pattern
- explicit verification instead of plausible-looking output
- heuristic runtime-state compaction instead of fake token introspection

## Derived Repo Generation

New repositories are generated from the same runtime model:

- choose an archetype and primary stack
- select manifests and optional repo features
- render templates, generated profiles, and runtime continuity tooling
- defer substantial root README/docs content by default until implementation has real structure
- preserve Compose names, port bands, and data-isolation defaults from the chosen manifests
- start work in the generated repo with the same boot sequence and continuity rules

See `docs/ARCHITECTURE_MAP.md` for the full system visual map, `docs/architecture-mental-model.md` for focused companion diagrams, and `docs/usage/STARTING_NEW_PROJECTS.md` for the operator workflow.
