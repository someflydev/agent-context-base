# Archetype Router

Purpose: infer the project shape so assistants load the right doctrine, workflows, and examples.

## Archetype Priority

Use the archetype declared in `manifests/repo.profile.yaml` unless repo signals clearly prove it is stale.

## Archetype Signals

| Archetype | Signals |
| --- | --- |
| `prompt-first-repo` | `.prompts/`, operator guides, ordered prompt docs, little or no product code |
| `backend-api` | API handlers, service entrypoint, schemas, request/response tests |
| `cli-tool` | command tree, subcommands, parser wiring, terminal-oriented tests |
| `data-pipeline` | batch jobs, transforms, schedules, dataset outputs, seed/reset flows |
| `local-rag-system` | indexing jobs, chunking/embedding pipeline, retrieval UI or API |
| `multi-storage-experiment` | many storage engines, compare/contrast docs, catalog or benchmark code |
| `polyglot-lab` | multiple language subprojects used intentionally |
| `dokku-deployable-web-service` | Procfile, Dockerfile, app packaging, web process, runtime env management |

## Composition Rules

Common valid compositions:

- `backend-api` + `dokku-deployable-web-service`
- `prompt-first-repo` + `polyglot-lab`
- `data-pipeline` + `multi-storage-experiment`
- `local-rag-system` + `backend-api`

If more than one archetype seems primary and the composition is not explicit, stop and clarify.

## Load Guidance

Load one primary archetype pack first. Add a secondary archetype only when it changes task behavior materially.

Examples:

- Adding a route to a FastAPI service: load `backend-api`, not `dokku-deployable-web-service`, unless deploy packaging changes too.
- Adding a Procfile and release task: load `dokku-deployable-web-service` plus the active backend archetype.
- Editing prompt sequences in a meta-runner repo: load `prompt-first-repo`, not backend archetypes.
