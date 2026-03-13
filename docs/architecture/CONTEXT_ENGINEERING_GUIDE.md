# Context Engineering Guide

Context engineering in this repo means controlling what the assistant loads, why it loads it, and when it should stop loading more.

## Core Principles

- Start narrow. More context is usually worse, not safer.
- Load by question, not by directory.
- Keep authority boundaries clear: doctrine, manifests, examples, templates, and memory do different jobs.
- Prefer one dominant example over blended patterns.
- Compress state into `MEMORY.md`; do not keep a running transcript in active context.

## Which Artifact Solves Which Problem

| Need | Best source |
| --- | --- |
| Stable rules or guardrails | `context/doctrine/` |
| Task sequence | `context/workflows/` |
| Framework or infra specifics | `context/stacks/` |
| Repo shape | `context/archetypes/` |
| Smallest justified bundle | `manifests/` |
| Preferred implementation pattern | `examples/` |
| Bootstrap scaffold | `templates/` |
| Current working state | `MEMORY.md` or a handoff snapshot |

## Minimal Bundle Heuristic

The first-pass bundle should usually contain:

1. one router
2. one anchor if helpful
3. only the relevant doctrine
4. one workflow
5. one archetype if needed
6. the active stack packs
7. one canonical example

If you cannot explain why a file is in the bundle, it probably should not be there.

## Valid Reasons To Expand Context

- the task crosses a new storage, queue, search, or deployment boundary
- the current workflow exposes a new verification need
- the first canonical example does not cover the changed surface
- local code shows a project-specific pattern that the first bundle missed

Expansion should happen one artifact at a time. If the route is still ambiguous after that, stop instead of broadening the bundle again.

## Compression Rules

Use `MEMORY.md` to keep:

- current objective
- active working set
- important decisions
- unresolved risks
- next concrete step

Do not use it for:

- durable doctrine
- full command transcripts
- stale exploration history
- broad repo summaries unrelated to the current task

## Failure Pattern To Avoid

The common failure mode is "load more because the assistant feels uncertain." In this system, uncertainty is usually a routing problem or a missing verification decision. Solve that first.

See `docs/usage/ASSISTANT_BEHAVIOR_SPEC.md` for normative rules and `context/doctrine/context-complexity-budget.md` for the underlying control philosophy.
