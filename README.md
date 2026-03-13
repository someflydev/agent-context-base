# agent-context-base

Prompt-first repository foundation for AI-assisted development with small context bundles, verified examples, and deterministic repo bootstrap.

`agent-context-base` is not an app template and not a prompt dump. It is a context system for building repos that humans and assistants can both navigate reliably. The repository separates durable rules, task playbooks, stack guidance, project-shape guidance, canonical examples, and generation templates so assistants can load less context and still make better decisions.

## Why This Exists

AI-assisted development fails in predictable ways: assistants scan too much, mix incompatible patterns, lose track of active state, and claim progress without proving the changed boundary. This repo exists to make that behavior harder. It gives you routing docs, machine-readable manifests, verified canonical examples, bootstrap tooling, and continuity patterns such as `MEMORY.md` and handoff snapshots.

## Key Capabilities

- Route normal-language tasks onto one workflow, one stack surface, and one archetype.
- Package the smallest useful context bundle with manifests instead of ad hoc browsing.
- Bootstrap new repos with `scripts/new_repo.py`, generated profiles, and isolated dev/test Compose layouts.
- Prefer canonical examples over improvised patterns, backed by verification metadata and harnesses.
- Preserve continuity across long sessions with `MEMORY.md`, stop-hook guidance, and handoff snapshots.

## Example Workflow

```bash
python scripts/new_repo.py analytics-api \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data
```

Then open the generated repo, read `AGENT.md` or `CLAUDE.md`, load the matching manifest and one canonical example, implement a vertical slice, verify it, and update `MEMORY.md` if the work will continue later.

## Supported Project Shapes

- Backend API services
- CLI tools
- Data pipelines
- Local RAG systems
- Multi-storage experiments
- Prompt-first meta repos
- Dokku-deployable services

First-class stacks include FastAPI, Hono/Bun, Rust/Axum, Go/Echo, Phoenix, Scala/Tapir/http4s/ZIO, Kotlin/http4k/Exposed, Nim/Jester/HappyX, plus supporting storage and infra packs such as Redis, MongoDB, DuckDB, Trino, NATS JetStream, Meilisearch, Elasticsearch, TimescaleDB, and Qdrant.

## Deeper Documentation

| Doc | Description |
| --- | --- |
| `docs/repo-purpose.md` | What this repository is for, what it is not for, and the core terms used throughout the system. |
| `docs/repo-layout.md` | Map of the top-level layers and where to look for doctrine, manifests, examples, templates, and scripts. |
| `docs/context-boot-sequence.md` | Deterministic startup contract for assistants working inside this repo or a derived repo. |
| `docs/session-start.md` | Short operational checklist for beginning or resuming a task. |
| `docs/architecture/ASSISTANT_RUNTIME_MODEL.md` | High-level architecture of the assistant runtime, including routing, manifests, examples, verification, and continuity. |
| `docs/architecture/CONTEXT_ENGINEERING_GUIDE.md` | Principles for keeping context small, high-signal, and explainable. |
| `docs/usage/STARTING_NEW_PROJECTS.md` | Practical guide for using this base to classify an idea, generate a repo, and start implementation. |
| `docs/usage/ASSISTANT_BEHAVIOR_SPEC.md` | Normative behavior contract for assistants operating in repos derived from this system. |
| `docs/usage/ADVANCED_ASSISTANT_OPERATIONS.md` | Guidance for long-running sessions, multi-agent work, cross-repo coordination, and higher-autonomy workflows. |
| `docs/memory-layer-overview.md` | How `MEMORY.md`, stop hooks, and handoff snapshots fit into the runtime. |
| `docs/deployment-readiness-checklists.md` | Concise deployment and release-readiness checks for service and prompt-first repos. |
| `docs/assistant-failure-modes.md` | Common failure patterns and the repo features that mitigate them. |
| `docs/architecture-mental-model.md` | Small set of diagrams showing runtime flow, repo generation, verification, and multi-agent coordination. |
| `docs/context-evolution.md` | Changelog of durable architectural changes to the base itself. |

## How To Understand This Repository

Start with `AGENT.md` or `CLAUDE.md`, then read the boot sequence and repo map. After that, inspect one manifest under `manifests/`, one preferred example under `examples/`, and the corresponding validation tools under `scripts/` and `verification/`.

If you want to see the system in action, these commands are the fastest entrypoints:

```bash
python scripts/preview_context_bundle.py backend-api-fastapi-polars --show-weights --show-anchors
python scripts/prompt_first_repo_analyzer.py .
python scripts/validate_context.py
python scripts/run_verification.py --tier fast
```
