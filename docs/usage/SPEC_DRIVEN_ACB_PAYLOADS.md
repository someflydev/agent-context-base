# Spec-Driven `.acb` Payloads

Generated repos now receive a repo-local `.acb/` payload that makes spec-driven development and validation-driven autonomy concrete instead of implied.

## Why This Exists

The generated repo should be able to answer these questions without reaching back into the source base repo:

- what kind of repo is this
- what constraints apply here
- what must be validated before a task is complete
- what should an assistant read first after a long break
- how should work be extended safely without drifting from the intended shape

That is the job of the local `.acb/` payload.

## Canonical Source Layout

Canonical source material lives in three places:

- `context/specs/`: layered narrative modules for product, architecture, agent behavior, and evolution
- `context/validation/`: layered narrative modules for validation expectations
- `context/acb/profile-rules.json`: machine-readable composition rules, inferred capabilities, doctrine mappings, and validation gates

This matches the existing `agent-context-base` philosophy:

- context stays layered
- manifests still select repo shape
- doctrine still constrains behavior
- routers still narrow startup
- validation remains the main safety rail

## Generated Repo Layout

The synthesized repo-local payload is written under `.acb/`:

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
  doctrines/
    ACTIVE_DOCTRINES.md
  routers/
    README.md
```

The generated repo may also keep vendored `.acb/context/`, `.acb/examples/`, `.acb/templates/`, `.acb/scripts/`, and `.acb/manifests/base/` paths when the manifest-selected support bundle calls for them.

## Composition Model

Composition is explicit and inspectable.

1. Manifests still pick the repo shape and vendored support context.
2. `scripts/acb_payload.py` infers active doctrines, routers, and capabilities from archetype, stack, selected manifests, support services, and deployment mode.
3. Canonical modules from `context/specs/` and `context/validation/` are selected by convention.
4. Those modules are composed into a small set of synthesized repo-local specs under `.acb/specs/`.
5. Machine-readable validation gates are emitted to `.acb/validation/MATRIX.json`, with a session-usable checklist in `.acb/validation/CHECKLIST.md`.
6. `.acb/INDEX.json` records the canonical source files and hashes so future drift or coverage tooling has a stable starting point.

## First-Read Order For Future Sessions

Inside a generated repo, assistants should read in this order:

1. `AGENT.md`
2. `CLAUDE.md`
3. `.acb/SESSION_BOOT.md`
4. `.acb/profile/selection.json`
5. `.acb/specs/AGENT_RULES.md`
6. `.acb/specs/VALIDATION.md`
7. `.acb/validation/CHECKLIST.md`
8. `.acb/generation-report.json`
9. `.prompts/*.txt` if present
10. vendored manifests and support docs if the current task needs them

This keeps startup narrow while still making autonomy bounded and resumable.

## Exercise The Flow

Generate a repo and inspect the local payload:

```bash
python scripts/new_repo.py analytics-api \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data \
  --target-dir /tmp/analytics-api

find /tmp/analytics-api/.acb -maxdepth 2 -type f | sort
```

Compose a payload directly without generating a whole repo:

```bash
python scripts/acb_payload.py \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --manifest backend-api-fastapi-polars \
  --support-service postgres \
  --output-dir /tmp/analytics-api
```

## Selection Examples

Backend API + FastAPI:

- archetype: `backend-api-service`
- primary stack: `python-fastapi-uv-ruff-orjson-polars`
- typical capabilities: `api`, `storage`, `frontend`
- validation pressure: route contracts, readiness, storage round-trips, UI-fragment correctness when present

CLI-heavy utility:

- archetype: `cli-tool`
- primary stack: `prompt-first-repo` or a future CLI-native stack
- typical capabilities: `cli`
- validation pressure: help output, exit codes, error-path behavior, prompt/profile integrity when prompt-first

Scrape/sync/classify data repo:

- archetype: `data-acquisition-service`
- primary stack: often `python-fastapi-uv-ruff-orjson-polars`
- typical capabilities: `api`, `workers`, `pipelines`, `scraping`, `storage`
- validation pressure: fetch-to-persist proof, replay safety, normalization fidelity, worker readiness

Evented multi-service lab or sync platform:

- archetype: `multi-source-sync-platform` or `multi-backend-service`
- primary stack: stack-specific service surfaces plus broker/storage support
- typical capabilities: `api`, `workers`, `pipelines`, `eventing`, `storage`
- validation pressure: seam contracts, checkpoint durability, event flow, cross-service or cross-source coordination proof

## Lightweight By Design

This system intentionally does not yet implement:

- full drift reconciliation
- spec graph compilation
- validation coverage scoring
- worktree-aware multi-agent orchestration

But the generated `.acb/INDEX.json`, `.acb/profile/selection.json`, and `.acb/validation/MATRIX.json` are structured so those capabilities can be added later without redesigning the payload model.
