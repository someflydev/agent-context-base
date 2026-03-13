# Assistant Behavior Specification

This is the normative behavior contract for assistants working in this repo and repos derived from it.

Normative language:

- `MUST`: required
- `SHOULD`: expected unless the repo gives a concrete reason to differ
- `MUST NOT`: prohibited

## Required Behavior

- The assistant MUST follow `docs/context-boot-sequence.md` before broad exploration.
- The assistant MUST treat context as a constrained resource.
- The assistant MUST prefer one workflow, one active stack surface, one archetype when needed, and one canonical example.
- The assistant MUST use routers and manifests when they exist.
- The assistant MUST verify the changed boundary instead of claiming correctness from plausible generation.
- The assistant MUST preserve repository structure, naming clarity, manifest integrity, and dev/test isolation unless the task explicitly changes them.
- The assistant MUST use `MEMORY.md` and handoff snapshots only as continuity artifacts, never as doctrine.
- The assistant MUST stop when routing, stack choice, archetype choice, verification posture, or isolation behavior remains ambiguous.

## Prohibited Behavior

- The assistant MUST NOT start by scanning whole directories.
- The assistant MUST NOT treat templates as canonical examples.
- The assistant MUST NOT merge several near-match manifests without an explicit reason.
- The assistant MUST NOT widen scope to resolve uncertainty that should instead trigger a stop condition.
- The assistant MUST NOT describe verification as complete when tests, harnesses, or checks were not actually run.

## Planning And Execution

- The assistant SHOULD plan before large or multi-boundary changes.
- The plan SHOULD name the objective, active workflow, stack or archetype surfaces, expected files, canonical example, verification path, and stop conditions.
- The assistant SHOULD work in reviewable vertical slices rather than broad speculative rewrites.
- The assistant SHOULD update docs, manifests, or continuity artifacts in the same slice when the implementation changed their truth.

## Long-Running Sessions

- The assistant SHOULD prune stale context after major phases.
- `MEMORY.md` SHOULD capture current objective, working set, decisions, verification status, and next step.
- A handoff snapshot SHOULD be created when another session, assistant, or person is likely to continue the work.

## Multi-Agent And Cross-Repo Work

- Shared continuity artifacts MUST stay concise and current.
- Each assistant SHOULD own a clear boundary or worktree when working in parallel.
- Cross-repo work MUST keep the role of each repo explicit: base repo for guidance and generation, project repo for product implementation.

See `docs/usage/ADVANCED_ASSISTANT_OPERATIONS.md` for longer-running and multi-agent patterns.
