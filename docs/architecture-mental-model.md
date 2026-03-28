# Architecture Mental Model

This document is the visual companion to `docs/architecture/ASSISTANT_RUNTIME_MODEL.md`.

## Assistant Runtime

```mermaid
flowchart LR
    A[User request] --> B[Repo signals and boot docs]
    B --> C[work.py resume]
    C --> D[TASK.md + SESSION.md + optional runtime memory / PLAN.md]
    D --> E[Routers]
    E --> F[Manifest]
    F --> G[Minimal context bundle]
    G --> H[Canonical example]
    H --> I[Implementation slice]
    I --> J[work.py checkpoint]
    J --> K[Verification]
```

The assistant does not jump from request to code. Runtime-state rehydration, routing, and manifest selection happen first.

## Repo Generation

```mermaid
flowchart LR
    A[Operator picks archetype and stack] --> B[scripts/new_repo.py]
    B --> C[Selected manifests]
    B --> D[Templates]
    C --> E[Generated profiles, work.py, and defaults]
    D --> E
    E --> F[Derived repo with AGENT.md, CLAUDE.md,<br/>generated profiles, code, Compose,<br/>optional tests, and later-earned front docs]
```

This matches the code in `scripts/new_repo.py`: manifests supply defaults and operational metadata, while templates supply the initial file content. Front-facing README and docs content are now intentionally deferred by default.

## Verification Loop

```mermaid
flowchart TB
    A[Docs, manifests, examples, templates, scripts] --> B[scripts/validate_context.py]
    B --> C[Manifest checks]
    B --> D[Catalog and router checks]
    B --> E[Bootstrap invariant checks]
    A --> F[scripts/run_verification.py]
    F --> G[Unit, script, and example suites]
```

The repo stays healthy because it validates both metadata integrity and runnable example behavior.

## Multi-Agent Coordination

```mermaid
flowchart LR
    A[Lead assistant] --> B[Shared objective and stop conditions]
    B --> C[Feature worktree]
    B --> D[Verification worktree]
    B --> E[Docs worktree]
    C --> F[Shared TASK.md / SESSION.md / runtime memory or handoff]
    D --> F
    E --> F
    F --> G[Merge and rerun verification]
```

This is a coordination pattern, not built-in automation. Each assistant owns one slice, then the shared continuity artifact records what can be merged next.
