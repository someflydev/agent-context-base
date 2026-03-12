# Archetype Router

Infer project shape from the repo goal, not only from language choice.

## Common Archetype Mappings

- routing docs, manifests, templates, prompt packs, repo bootstrap
  - `context/archetypes/prompt-first-repo.md`
- HTTP service, API routes, handlers, backing storage
  - `context/archetypes/backend-api-service.md`
- command tree, flags, shell-facing behavior
  - `context/archetypes/cli-tool.md`
- ingestion, transforms, analytics outputs
  - `context/archetypes/data-pipeline.md`
- retrieval, chunking, indexing, embeddings
  - `context/archetypes/local-rag-system.md`
- many storage backends compared intentionally
  - `context/archetypes/multi-storage-experiment.md`
- multiple language surfaces in one repo
  - `context/archetypes/polyglot-lab.md`
- single deployable service with Dokku emphasis
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
- "Compare MongoDB and Elasticsearch in one experimental repo"
  - `context/archetypes/multi-storage-experiment.md`

## Guardrails

- archetype is about project shape, not just framework choice
- use one primary archetype unless the repo is intentionally composite
- if two archetypes compete, choose the one that best matches the user-visible goal

