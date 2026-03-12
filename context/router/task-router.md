# Task Router

Purpose: map normal English requests to the smallest relevant context bundle.

## Core Rule

Infer the task from the request itself. Do not require the human to remember workflow, stack, or manifest names.

## Routing Sequence

1. Classify the request by verb.
2. Identify the dominant nouns.
3. Confirm the active archetype.
4. Confirm the active stack.
5. Load the smallest bundle that can safely support the task.

## Verb Heuristics

| Verb family | Default workflow |
| --- | --- |
| add, build, create, implement | `context/workflows/add-feature.md` |
| fix, debug, repair | `context/workflows/fix-bug.md` |
| refactor, simplify, clean up, reorganize | `context/workflows/refactor.md` |
| bootstrap, start, scaffold | `context/workflows/bootstrap-repo.md` |
| generate prompts, create prompt sequence | `context/workflows/generate-prompt-sequence.md` |
| tighten after run, refine, harden, post-flight | `context/workflows/post-flight-refinement.md` |
| add smoke test, verify startup, add health check | `context/workflows/add-smoke-tests.md` |
| add endpoint, add route, add handler | `context/workflows/add-api-endpoint.md` |
| add seed data, seed fixture, reset sample data | `context/workflows/add-seed-data.md` |
| add deploy, package for dokku, add Procfile | `context/workflows/add-deployment-support.md` |
| extend cli, add command, add subcommand | `context/workflows/extend-cli.md` |
| add rag, index docs, embed corpus | `context/workflows/add-local-rag-indexing.md` |
| add storage, add redis, add mongo, add search, add queue | `context/workflows/add-storage-integration.md` |

## Noun Heuristics

| Noun or phrase | Extra context |
| --- | --- |
| endpoint, handler, route, middleware | API workflow and backend archetype |
| prompt, sequence, operator guide | prompt-first archetype |
| smoke, health, startup, check | smoke-test doctrine and workflow |
| compose, docker, volume, port, env | compose isolation doctrine and docker stack pack |
| dokku, Procfile, app.json, deploy | Dokku doctrine and deployment workflow |
| redis, keydb, mongo | storage workflow plus `context/stacks/redis-mongodb.md` |
| duckdb, trino, polars | storage workflow plus `context/stacks/trino-duckdb-polars.md` |
| nats, jetstream, meilisearch | storage workflow plus `context/stacks/nats-jetstream-meilisearch.md` |
| timescaledb, elasticsearch, qdrant | storage workflow plus `context/stacks/timescaledb-elasticsearch-qdrant.md` |
| rag, embeddings, index, chunking | local-rag archetype and RAG workflow |
| htmx, plotly, fragment, chart | stack-specific UI patterns inside the active backend stack |

## Smallest Relevant Bundle First

Default first bundle:

1. `manifests/repo.profile.yaml`
2. `context/doctrine/00-core-principles.md`
3. `context/doctrine/09-context-loading-rules.md`
4. one workflow
5. one archetype
6. one or more active stack packs
7. one preferred canonical example

Do not load more until a concrete gap appears.

## Escalation Logic

Escalate only when one of these is true:

- the target stack is ambiguous
- the target archetype is ambiguous
- the task crosses storage or service boundaries
- the task changes deployment behavior
- the task requires a new canonical example because no valid one exists

## Anti-Hallucination Rules

- If the repo already contains the target pattern, prefer local code over prose docs.
- If the manifest and repo disagree, say so and stop.
- If the task touches persistence, queues, search, or cross-service boundaries, require smoke tests and minimal real-infra integration tests.
- Never assume default ports.
- Never assume test data may share env files, volumes, or seed flows with dev.

## Example Request Mappings

| Request | Bundle |
| --- | --- |
| "Add a JSON endpoint for daily metrics in the FastAPI service." | doctrine `00,01,02,03`; workflow `add-api-endpoint`; archetype `backend-api`; stack `python-fastapi-polars-htmx-plotly`; examples `api-endpoints`, `smoke-tests` |
| "Wire a Redis cache into this Hono service." | doctrine `00,02,03,04`; workflow `add-storage-integration`; archetype `backend-api`; stacks `typescript-hono-bun-drizzle-tsx`, `redis-mongodb`; examples `storage-integration`, `docker-compose`, `smoke-tests` |
| "Create the first prompt sequence for this repo." | doctrine `00,06,07,09`; workflow `generate-prompt-sequence`; archetype `prompt-first-repo`; stack `prompt-first-repo-support`; examples `prompt-first` |
| "Package this Echo app for Dokku." | doctrine `00,04,10`; workflow `add-deployment-support`; archetype `dokku-deployable-web-service`; stacks `go-echo-templ`, `docker-compose-dokku`; examples `dokku-deployment`, `docker-compose` |
| "Add a smoke test for startup and health." | doctrine `00,02,03,04`; workflow `add-smoke-tests`; active archetype; active stack; examples `smoke-tests` |
| "Bootstrap a local RAG repo around FastAPI and Qdrant." | doctrine `00,02,03,04,07,09,10`; workflows `bootstrap-repo`, `add-local-rag-indexing`; archetype `local-rag-system`; stacks `python-fastapi-polars-htmx-plotly`, `timescaledb-elasticsearch-qdrant`, `docker-compose-dokku`; examples `local-rag`, `docker-compose`, `smoke-tests` |
| "Refactor the compose layout so dev and test can run side by side." | doctrine `00,04,09`; workflow `refactor`; archetype current repo archetype; stack `docker-compose-dokku`; examples `docker-compose`, `smoke-tests` |
