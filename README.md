# agent-context-base

`agent-context-base` is a context-first foundation for generating and running assistant-friendly repositories. It is not an app template and not a prompt dump. It is a system for keeping specs, validation rules, canonical examples, repo generation, and session startup narrow enough that long autonomous sessions stay trustworthy.

## What Problem It Solves

Assistant-led development drifts when context is loaded loosely, validation is implied instead of stated, and a later session has to rediscover repo intent from scratch. This repo addresses that by keeping:

- canonical specs under [`context/specs/`](context/specs/README.md)
- canonical validation narratives under [`context/validation/`](context/validation/README.md)
- machine-readable composition rules under [`context/acb/profile-rules.json`](context/acb/profile-rules.json)
- generation and inspection tooling under [`scripts/README.md`](scripts/README.md)
- verification coverage under [`verification/README.md`](verification/README.md)

## What “Context-First” Means Here

Context-first means assistants should read the smallest stable context surface that can still explain:

- what this repo is
- what shape it is supposed to have
- what boundary is currently being changed
- what proof is required before claiming completion

The goal is explicit over implicit: route first, then load only the active workflow, stack surface, archetype, examples, and validation path.

## `.acb/` In Generated Repos

Generated repos keep their repo-local operating bundle under `.acb/`. That hidden directory is the continuity boundary between canonical source material in this base repo and the child repo’s local startup surface.

Typical generated layout:

```text
.acb/
  README.md
  SESSION_BOOT.md
  INDEX.json
  profile/
    selection.json
  specs/
    PRODUCT.md
    ARCHITECTURE.md
    AGENT_RULES.md
    VALIDATION.md
    EVOLUTION.md
  validation/
    CHECKLIST.md
    MATRIX.json
    COVERAGE.md
    COVERAGE.json
  doctrines/
    ACTIVE_DOCTRINES.md
  routers/
    README.md
  scripts/
    acb_inspect.py
    acb_verify.py
```

Why it exists:

- future sessions can rehydrate locally without reopening the base repo
- spec-driven and validation-driven work becomes explicit
- origin metadata and hashes make drift visible
- coverage summaries make validation gaps visible

## Spec-Driven And Validation-Driven Development

The system composes canonical product, architecture, agent, evolution, and validation modules into repo-local `.acb/specs/*.md` files. Validation is treated as a first-class autonomy rail, not a trailing note.

Current hardening features:

- canonical source headers on spec and validation modules
- `.acb/INDEX.json` with source metadata and hashes
- `.acb/validation/COVERAGE.json` and `.acb/validation/COVERAGE.md`
- `.acb/scripts/acb_inspect.py` for visibility
- `.acb/scripts/acb_verify.py` for local payload drift, optional canonical drift, and coverage gaps

## First 10 Minutes

1. Read [`AGENT.md`](AGENT.md) or [`CLAUDE.md`](CLAUDE.md).
2. Read [`docs/context-boot-sequence.md`](docs/context-boot-sequence.md).
3. Read [`docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md`](docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md).
4. Inspect available shapes with `python scripts/new_repo.py --list-archetypes` and `python scripts/new_repo.py --list-stacks`.
5. Preview a bundle with `python scripts/preview_context_bundle.py backend-api-fastapi-polars --show-weights --show-anchors`.
6. Generate a repo and start a fresh session inside that generated repo.

Example:

```bash
python scripts/new_repo.py analytics-api \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --manifest backend-api-fastapi-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data \
  --initial-prompt-file /tmp/operator-brief.txt \
  --target-dir /tmp/analytics-api
```

Inside the generated repo, the recommended first read order is:

1. `AGENT.md`
2. `CLAUDE.md`
3. `.acb/SESSION_BOOT.md`
4. `.acb/profile/selection.json`
5. `.acb/specs/AGENT_RULES.md`
6. `.acb/specs/VALIDATION.md`
7. `.acb/validation/CHECKLIST.md`
8. `.acb/validation/COVERAGE.md`
9. `.acb/generation-report.json`

## Diagrams And Deeper Docs

- [`docs/ARCHITECTURE_MAP.md`](docs/ARCHITECTURE_MAP.md)
- [`docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md`](docs/usage/SPEC_DRIVEN_ACB_PAYLOADS.md)
- [`docs/usage/ASSISTANT_BEHAVIOR_SPEC.md`](docs/usage/ASSISTANT_BEHAVIOR_SPEC.md)
- [`docs/usage/STARTING_NEW_PROJECTS.md`](docs/usage/STARTING_NEW_PROJECTS.md)
- [`scripts/README.md`](scripts/README.md)
- [`verification/README.md`](verification/README.md)

## Verification Commands

```bash
python scripts/validate_context.py
python scripts/run_verification.py --tier fast
python scripts/acb_payload.py \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --manifest backend-api-fastapi-polars \
  --support-service postgres \
  --output-dir /tmp/analytics-api
```
