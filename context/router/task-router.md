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
- "integration test", "real db test", "docker-backed test"
  - load `context/workflows/add-storage-integration.md`
- "bootstrap a repo", "new repo from base", "starter repo"
  - load `context/workflows/bootstrap-repo.md`
  - prefer `scripts/new_repo.py` when the task is repo generation instead of a manual copy pass
- "make a prompt sequence", "split this into prompts"
  - load `context/workflows/generate-prompt-sequence.md`
- "deploy", "Dokku", "Procfile", "release phase"
  - load `context/workflows/add-deployment-support.md`
- "seed data", "fixtures", "sample records"
  - load `context/workflows/add-seed-data.md`
- "new endpoint", "new route", "new handler"
  - load `context/workflows/add-api-endpoint.md`
- "research candidate public data sources", "evaluate data sources", "find a usable dataset"
  - load `context/workflows/research-data-sources.md`
- "add a new API source", "pull from an API", "ingest an API feed"
  - load `context/workflows/add-api-ingestion-source.md`
- "add a scraper", "scrape this site", "ingest by scraping"
  - load `context/workflows/add-scraping-source.md`
- "save raw downloads", "retain raw payloads", "archive raw responses"
  - load `context/workflows/add-raw-download-archive.md`
- "parse raw payloads", "normalize source data", "build a parser"
  - load `context/workflows/add-parser-normalizer.md`
- "classify records", "categorize records", "add enrichment"
  - load `context/workflows/add-classification-step.md`
- "build a twice-daily sync", "schedule recurring syncs", "run this every day"
  - load `context/workflows/add-recurring-sync.md`
- "use events to coordinate syncs", "event-driven sync", "publish source sync events"
  - load `context/workflows/add-event-driven-sync.md`
- "add backoff", "handle rate limits", "retry this source safely"
  - load `context/workflows/add-source-backoff-retry.md`
- "new command", "CLI flag", "subcommand"
  - load `context/workflows/extend-cli.md`
- "local rag", "index docs", "retrieval"
  - load `context/workflows/add-local-rag-indexing.md`
- "add redis", "connect postgres", "wire search", "storage integration"
  - load `context/workflows/add-storage-integration.md`
- "post-flight", "cleanup this pass", "refine before commit"
  - load `context/workflows/post-flight-refinement.md`

## Compound Requests

If a request spans two workflows, pick the dominant one first and load the second only if needed.

Examples:

- "Add an endpoint backed by Redis"
  - start with `context/workflows/add-api-endpoint.md`
  - then load `context/workflows/add-storage-integration.md`
- "Bootstrap a repo and generate prompt files"
  - start with `context/workflows/bootstrap-repo.md`
  - then load `context/workflows/generate-prompt-sequence.md`
- "Add a storage-backed route plus a real integration test"
  - start with `context/workflows/add-api-endpoint.md`
  - then load `context/workflows/add-storage-integration.md`
- "Add a new API source and keep raw payloads for later parsing"
  - start with `context/workflows/add-api-ingestion-source.md`
  - then load `context/workflows/add-raw-download-archive.md`
- "Research candidate public data sources and pick between API versus scraping"
  - start with `context/workflows/research-data-sources.md`
  - then load `context/workflows/add-api-ingestion-source.md` or `context/workflows/add-scraping-source.md`
- "Schedule twice-daily syncs and coordinate them with events"
  - start with `context/workflows/add-recurring-sync.md`
  - then load `context/workflows/add-event-driven-sync.md`
- "Clean up the implementation before commit"
  - start with `context/workflows/post-flight-refinement.md`

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
- "Save raw downloads so I can re-parse them later"
  - workflow: `context/workflows/add-raw-download-archive.md`
- "Build a twice-daily sync for these sources"
  - workflow: `context/workflows/add-recurring-sync.md`
- "Research candidate public data sources before we implement anything"
  - workflow: `context/workflows/research-data-sources.md`
- "Classify records after parsing"
  - workflow: `context/workflows/add-classification-step.md`
- "Use events to coordinate source syncs"
  - workflow: `context/workflows/add-event-driven-sync.md`
- "Make this generated repo less sloppy before I commit"
  - workflow: `context/workflows/post-flight-refinement.md`

## Stop And Clarify Internally

Stop expanding context when the task is already clearly mapped. Do not load every workflow "just in case."
