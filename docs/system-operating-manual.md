# System Operating Manual

Use this document as the short operational reference after you already understand the repo purpose and boot sequence.

## One-Page Operating Model

`user request -> routers -> manifest -> minimal bundle -> canonical example -> implementation slice -> verification -> continuity update`

## Working Rules

- Start from the boot sequence, not from a broad scan.
- Let routers and manifests narrow the task before loading examples or templates.
- Prefer one workflow, one stack surface, and one canonical example.
- Verify the changed boundary before claiming progress.
- Keep `MEMORY.md` short, current, and state-oriented.
- Create a handoff snapshot when another session is likely.
- Stop when ambiguity would force broad context loading.

## Where To Look Next

- Runtime model: `docs/architecture/ASSISTANT_RUNTIME_MODEL.md`
- Behavior contract: `docs/usage/ASSISTANT_BEHAVIOR_SPEC.md`
- Project bootstrap: `docs/usage/STARTING_NEW_PROJECTS.md`
- Advanced operations: `docs/usage/ADVANCED_ASSISTANT_OPERATIONS.md`
- Memory and handoffs: `docs/memory-layer-overview.md`
