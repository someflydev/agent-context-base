# Archetype Router

Infer project shape from the repo goal, not only from language choice.

## Common Archetype Mappings

- routing docs, manifests, templates, prompt packs, generated profiles, repo bootstrap
  - `context/archetypes/prompt-first-repo.md`
- HTTP service, API routes, handlers, backing storage
  - `context/archetypes/backend-api-service.md`
- command tree, flags, shell-facing behavior
  - `context/archetypes/cli-tool.md`
- ingestion, transforms, analytics outputs
  - `context/archetypes/data-pipeline.md`
- source adapters, raw archival, parsing, normalization, enrichment, persistence
  - `context/archetypes/data-acquisition-service.md`
- multiple sources, recurring syncs, event coordination, source health, replay
  - `context/archetypes/multi-source-sync-platform.md`
- retrieval, chunking, indexing, embeddings
  - `context/archetypes/local-rag-system.md`
- many storage backends compared intentionally
  - `context/archetypes/multi-storage-experiment.md`
- multiple language surfaces in one repo
  - `context/archetypes/polyglot-lab.md`
- single deployable service with Dokku emphasis, `Procfile`, `app.json`, or release commands
  - `context/archetypes/dokku-deployable-service.md`

## Routing Examples

- "Create a new prompt-driven starter repo"
  - `context/archetypes/prompt-first-repo.md`
- "Build an API service with FastAPI and Redis"
  - `context/archetypes/backend-api-service.md`
- "Add a subcommand for local data export"
  - `context/archetypes/cli-tool.md`
- "Index notes into Qdrant and answer questions locally"
  - `context/archetypes/local-rag-system.md`
- "Build a service that acquires and normalizes public data"
  - `context/archetypes/data-acquisition-service.md`
- "Coordinate recurring syncs across multiple sources"
  - `context/archetypes/multi-source-sync-platform.md`
- "Compare MongoDB and Elasticsearch in one experimental repo"
  - `context/archetypes/multi-storage-experiment.md`
- "Set up a single service repo that will deploy to Dokku"
  - `context/archetypes/dokku-deployable-service.md`

## Guardrails

- archetype is about project shape, not just framework choice
- use one primary archetype unless the repo is intentionally composite
- if two archetypes compete, choose the one that best matches the user-visible goal
