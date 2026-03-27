# Architecture Map

This is the shortest accurate map of how `agent-context-base` currently works.

## System Shape

- canonical context and validation source files live under `context/`
- manifests and composition rules decide what should be loaded or generated
- `scripts/new_repo.py` generates descendant repos
- `scripts/acb_payload.py` composes the repo-local `.acb/` payload
- verification keeps examples, scripts, docs, and generation assumptions aligned

## Spec + Validation Flow

```mermaid
flowchart LR
    A[context/specs/] --> D[scripts/acb_payload.py]
    B[context/validation/] --> D
    C[context/acb/profile-rules.json] --> D
    D --> E[.acb/specs/*.md]
    D --> F[.acb/validation/CHECKLIST.md]
    D --> G[.acb/validation/MATRIX.json]
    D --> H[.acb/validation/COVERAGE.json]
    D --> I[.acb/INDEX.json]
    E --> J[assistant session]
    F --> J
    H --> J
    J --> K[implement]
    K --> L[validate]
    L --> M[commit or continue]
```

## `.acb` Composition Flow

```mermaid
flowchart TD
    A[archetype] --> E[selection]
    B[primary stack] --> E
    C[selected manifests] --> E
    D[support services] --> E
    E --> F[profile-rules.json]
    F --> G[doctrines]
    F --> H[routers]
    F --> I[capabilities]
    F --> J[validation gates]
    G --> K[.acb payload]
    H --> K
    I --> K
    J --> K
```

## Session Execution Loop

```mermaid
flowchart LR
    A[read AGENT.md and CLAUDE.md] --> B[read .acb/SESSION_BOOT.md]
    B --> C[read .acb/profile/selection.json]
    C --> D[read .acb/specs/AGENT_RULES.md and VALIDATION.md]
    D --> E[check CHECKLIST.md and COVERAGE.md]
    E --> F[plan one slice]
    F --> G[implement]
    G --> H[run validation]
    H --> I{proof passed?}
    I -->|yes| J[done]
    I -->|no, blocked| K[blocked]
    I -->|no, more work| L[incomplete]
```

## Future Direction

Clearly future-facing, not implemented yet:

```mermaid
flowchart TD
    A[canonical modules with origin metadata] --> B[source graph or DAG]
    B --> C[smarter recomposition]
    B --> D[targeted drift remediation]
    B --> E[coverage-aware planning]
```

## Directory Index

| Path | Current role |
| --- | --- |
| [`context/specs/`](../context/specs/README.md) | Canonical product, architecture, agent, and evolution modules. |
| [`context/validation/`](../context/validation/README.md) | Canonical validation narratives. |
| [`context/acb/`](../context/acb/README.md) | Machine-readable profile composition rules. |
| [`manifests/`](../manifests) | Bundle selection for routing and generation. |
| [`scripts/`](../scripts/README.md) | Generation, composition, inspection, and verification entrypoints. |
| [`verification/`](../verification/README.md) | Repository and example verification. |

## Recommended Follow-On Reads

1. [`docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md`](usage/SPEC_DRIVEN_ACB_PAYLOADS.md)
2. [`docs/usage/ASSISTANT_BEHAVIOR_SPEC.md`](usage/ASSISTANT_BEHAVIOR_SPEC.md)
3. [`scripts/README.md`](../scripts/README.md)
