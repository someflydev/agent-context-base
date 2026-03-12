# Task Router

Map ordinary requests onto the smallest useful workflow bundle.

## Core Rule

Route from what the user is trying to do, not from internal file names.

## Common Task Mappings

- "add a feature", "build this capability", "implement this flow"
  - load `context/workflows/add-feature.md`
- "fix a bug", "regression", "this is broken"
  - load `context/workflows/fix-bug.md`
- "refactor", "clean this up", "simplify this"
  - load `context/workflows/refactor.md`
- "add smoke tests", "happy-path check", "boot verification"
  - load `context/workflows/add-smoke-tests.md`
- "bootstrap a repo", "new repo from base", "starter repo"
  - load `context/workflows/bootstrap-repo.md`
- "make a prompt sequence", "split this into prompts"
  - load `context/workflows/generate-prompt-sequence.md`
- "deploy", "Dokku", "Procfile", "release phase"
  - load `context/workflows/add-deployment-support.md`
- "seed data", "fixtures", "sample records"
  - load `context/workflows/add-seed-data.md`
- "new endpoint", "new route", "new handler"
  - load `context/workflows/add-api-endpoint.md`
- "new command", "CLI flag", "subcommand"
  - load `context/workflows/extend-cli.md`
- "local rag", "index docs", "retrieval"
  - load `context/workflows/add-local-rag-indexing.md`
- "add redis", "connect postgres", "wire search", "storage integration"
  - load `context/workflows/add-storage-integration.md`

## Compound Requests

If a request spans two workflows, pick the dominant one first and load the second only if needed.

Examples:

- "Add an endpoint backed by Redis"
  - start with `context/workflows/add-api-endpoint.md`
  - then load `context/workflows/add-storage-integration.md`
- "Bootstrap a repo and generate prompt files"
  - start with `context/workflows/bootstrap-repo.md`
  - then load `context/workflows/generate-prompt-sequence.md`

## Routing Examples

- "Set up a FastAPI repo for a small analytics API"
  - workflow: `context/workflows/bootstrap-repo.md`
- "Add a Bun route that writes through Drizzle"
  - workflow: `context/workflows/add-api-endpoint.md`
- "Search results look wrong after indexing"
  - workflow: `context/workflows/fix-bug.md`
- "Give me a quick boot check before I deploy"
  - workflow: `context/workflows/add-smoke-tests.md`
- "Add a local vector index for docs"
  - workflow: `context/workflows/add-local-rag-indexing.md`

## Stop And Clarify Internally

Stop expanding context when the task is already clearly mapped. Do not load every workflow "just in case."

