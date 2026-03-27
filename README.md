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

Start in `agent-context-base`, launch Codex, Claude, or Gemini there, and give it a short 2-5 sentence project description. Do not try to guess the `scripts/new_repo.py` arguments first. In the normal flow, the assistant reads this repo's routing docs and option surfaces, proposes the right `new_repo.py` command, and you approve or refine it. `docs/usage/STARTING_NEW_PROJECTS.md` includes 100 example initial prompts you can reuse.

The generated repo can be created anywhere convenient, including a clean path such as `/tmp/analytics-api`, so the assistant is not working inside a half-prepared directory from the start.

Before generation, the assistant should make storage and broker choices explicit. If the prompt does not clearly name persistence, queue, search, or vector backends, the assistant should ask or propose a narrow supported set rather than silently accepting generic defaults. When the operator has an initial prompt, pass it through the generator so the generated repo keeps `.prompts/initial-prompt.txt`, starter implementation prompts, and the hidden `.acb/generation-report.json` audit snapshot.

Generated repos now defer a substantial root `README.md` and root `docs/` by default. Early boot guidance lives in `AGENT.md`, `CLAUDE.md`, and the generated profile so front-facing docs can be written later against implemented reality instead of speculation.

```bash
python scripts/new_repo.py analytics-api \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data \
  --initial-prompt-file /tmp/operator-brief.txt \
  --target-dir /tmp/analytics-api
```

After generation, change into the new repo, start a fresh assistant session there, and ask it to inspect the generated bootstrap context and propose the implementation plan before it starts coding. You review that plan, correct constraints or priorities if needed, and then let the assistant execute, verify the changed boundary, and keep you informed.

Strong first prompt inside the generated repo:

> Read the bootstrap context that matters for this repo, propose the implementation plan you intend to execute, wait for my approval, then carry it out with verification checkpoints.

## Supported Project Shapes

- Prompt-first meta repos
- Backend API services
- CLI tools
- Data pipelines
- Data acquisition services
- Multi-backend services
- Multi-source sync platforms
- Local RAG systems
- Multi-storage experiments
- Polyglot labs
- Dokku-deployable services

First-class stacks include FastAPI, Hono/Bun, Rust/Axum, Go/Echo, Phoenix, Scala/Tapir/http4s/ZIO, Kotlin/http4k/Exposed, Nim/Jester/HappyX, Clojure/Kit, Dart/Dartfrog, OCaml/Dream, Crystal/Kemal, Zig/Zap/Jetzig, and Ruby/Hanami, plus supporting infra packs such as Redis, MongoDB, DuckDB, DuckDB+Parquet, Trino, NATS JetStream, Kafka, RabbitMQ, Meilisearch, Elasticsearch, TimescaleDB, Qdrant, and MinIO.

## Deeper Documentation

| Doc | Description |
| --- | --- |
| `docs/repo-purpose.md` | What this repository is for, what it is not for, and the core terms used throughout the system. |
| `docs/ARCHITECTURE_MAP.md` | System architecture diagrams, component index, and full documentation map. |
| `docs/system-operating-manual.md` | One-page operational reference covering the end-to-end flow and working rules. |
| `docs/architecture/ASSISTANT_RUNTIME_MODEL.md` | High-level architecture of the assistant runtime, including routing, manifests, examples, verification, and continuity. |
| `docs/architecture/CONTEXT_ENGINEERING_GUIDE.md` | Principles for keeping context small, high-signal, and explainable. |
| `docs/usage/STARTING_NEW_PROJECTS.md` | Practical guide for using this base to classify an idea, generate a repo, and start implementation. |
| `docs/usage/ASSISTANT_BEHAVIOR_SPEC.md` | Normative behavior contract for assistants operating in repos derived from this system. |
| `docs/usage/ADVANCED_ASSISTANT_OPERATIONS.md` | Guidance for long-running sessions, multi-agent work, cross-repo coordination, and higher-autonomy workflows. |
| `docs/CONTRIBUTOR_PLAYBOOK.md` | Rules and checklists for extending the repo: new stacks, examples, archetypes, and verification coverage. |
| `docs/memory-layer-overview.md` | How `MEMORY.md`, stop hooks, and handoff snapshots fit into the runtime. |
| `docs/deployment-readiness-checklists.md` | Concise deployment and release-readiness checks for service and prompt-first repos. |
| `docs/assistant-failure-modes.md` | Common failure patterns and the repo features that mitigate them. |
| `docs/architecture-mental-model.md` | Small set of diagrams showing runtime flow, repo generation, verification, and multi-agent coordination. |
| `docs/context-evolution.md` | Changelog of durable architectural changes to the base itself. |

## How To Understand This Repository

Humans usually only need a small mental model here: this repo contains routing docs, manifests, examples, verification assets, and the generator used to create a new project repo. In normal use, the assistant loads `AGENT.md` or `CLAUDE.md`, picks the right manifests and examples, and runs the relevant utilities when needed. You are not expected to manually read every bootstrap file line by line before work starts.

If you want to spot-check what the assistant is doing, these are the most useful orientation commands:

```bash
python scripts/new_repo.py --list-archetypes
python scripts/new_repo.py --list-stacks
python scripts/preview_context_bundle.py backend-api-fastapi-polars --show-weights --show-anchors
python scripts/validate_context.py
```
