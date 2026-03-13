# Starting New Projects

Use this base in two phases:

1. classify and generate in `agent-context-base`
2. build the product in the generated repo

## The Two-Repo Model

`agent-context-base` is the planning and generation repo. It helps you choose the project shape, stack, manifests, and starter assets.

The generated repo is the product repo. That is where the real application code, repo-local examples, and project-specific verification should live.

## From Idea To Generated Repo

Start a coding assistant inside `agent-context-base` and give it a short 2-5 sentence project description. That first prompt should describe the product, the main user or operator, the primary interface, and any hard constraints that matter immediately.

The assistant should do the repo loading and synthesis. You are not expected to manually read `AGENT.md`, `CLAUDE.md`, manifests, or examples line by line before work starts. Your job is to validate direction, constraints, priorities, and the generated repo location.

Normal flow:

1. Start in `agent-context-base`.
2. Launch Codex, Claude, or Gemini there.
3. Give a short 2-5 sentence initial prompt.
4. Let the assistant inspect this repo and propose the `scripts/new_repo.py` arguments.
5. Review the proposed archetype, primary stack, optional flags, and target directory.
6. Generate the repo.

The `new_repo.py` arguments are usually produced after the assistant has inspected the base repo. They are not meant to be manually guessed first.

Useful commands:

```bash
python scripts/new_repo.py --list-archetypes
python scripts/new_repo.py --list-stacks
python scripts/new_repo.py --list-manifests
python scripts/preview_context_bundle.py backend-api-fastapi-polars --show-weights --show-anchors
```

Generated repos can live anywhere convenient. A clean path under `/tmp/...` is often the simplest choice while the repo is being created and bootstrapped.

Example:

```bash
python scripts/new_repo.py analytics-api \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data \
  --dokku \
  --target-dir /tmp/analytics-api
```

## What `new_repo.py` Actually Does

- picks the requested archetype and primary stack
- selects default manifests for that repo shape
- renders README, `AGENT.md`, `CLAUDE.md`, and generated profile files
- optionally renders prompt files, seed data, smoke tests, integration tests, and Dokku assets
- generates isolated `docker-compose.yml` and `docker-compose.test.yml` when the profile implies local infra

## First Steps In The Generated Repo

1. Change into the generated repo.
2. Start a fresh assistant session there.
3. Ask the assistant to inspect the generated bootstrap context and propose the implementation plan.
4. Review that plan and correct scope, constraints, or priorities before coding starts.
5. Let the assistant execute incrementally, verify each changed boundary, and keep you informed.
6. Create or update `MEMORY.md` if the work will continue later.

Strong first prompt for the generated repo:

> Read the bootstrap context that matters for this repo, propose the implementation plan you intend to execute, wait for my approval, then carry it out with verification checkpoints.

The assistant should load `AGENT.md` or `CLAUDE.md`, the generated profile, and the most relevant examples or manifests. The human should review the plan, not manually reconstruct the startup context file by file.

## Rules That Keep New Repos Clean

- pick one archetype first; do not start with a composite repo unless the product truly needs it
- pick one stack first; add more stacks only when the product boundary requires them
- keep examples and templates distinct
- let manifests and generated profiles narrow the first working set
- avoid carrying speculative future dependencies into the initial repo

## 50 Example Initial Prompts

Use these as starting points inside `agent-context-base`. Each one is intentionally short. Adjust domain details, constraints, and deployment expectations, then let the assistant translate the prompt into `new_repo.py` arguments.

1. I need a small analytics API for internal operations. It should expose a few HTTP endpoints, read batch data, and stay easy to test locally. Keep the first version narrow and biased toward simple verification.
2. Build a backend service for ingesting vendor CSV exports and serving normalized reports. The first milestone is deterministic local processing plus a health endpoint. Optimize for a clean vertical slice, not feature breadth.
3. I want a CLI tool that operators can run to reconcile two data sources. It should have explicit commands, readable output, and strong test coverage around the core comparison flow. Keep the initial repo lean.
4. Create a local RAG prototype for a private document set. It should index a small deterministic corpus and support a simple query flow. Favor local-only dependencies and repeatable smoke checks.
5. I need a prompt-first repo for drafting and validating prompt assets. The repo should emphasize structure, reviewability, and verification of generated outputs. Keep the workflow simple enough for one assistant session at a time.
6. Build a dokku-deployable service for lightweight report delivery. The first cut needs one route, one storage boundary, and clear deployment notes. Prefer boring defaults over clever abstractions.
7. I want a FastAPI-based backend for scheduled data enrichment. The first milestone is one job, one route to inspect results, and deterministic fixtures. Keep local setup small.
8. Create a Bun and Hono service for a lightweight internal API. It should stay fast to start, easy to test, and easy to read. Focus on one end-to-end slice first.
9. I need a Go service that exposes a health endpoint and one reporting workflow. The repo should be straightforward for assistant-led development and verification. Keep the initial surface intentionally narrow.
10. Build a Rust service with a small HTTP API and strong test boundaries. The first release only needs one core flow and local verification. Avoid premature layering.
11. Create a repo for transforming raw event files into normalized tables. The pipeline should be deterministic, fixture-driven, and easy to inspect. Start with one source and one output.
12. I need a backend repo for querying precomputed analytics results. It should prioritize fast local iteration, explicit schemas, and smoke tests. Keep the storage story simple in v1.
13. Build a local service for summarizing support tickets into weekly themes. It should ingest small fixture datasets and expose one report endpoint. The first plan should emphasize verification and change visibility.
14. Create a CLI repo for generating release notes from structured inputs. It should support one main command, deterministic sample data, and clear terminal output. Keep dependencies light.
15. I need a data pipeline for parsing partner exports and producing cleaned artifacts. The repo should start with one reliable transformation path and local tests. Bias toward explicit file layouts.
16. Build a local document indexing system for engineering notes. It should support indexing, querying, and deterministic smoke checks against a tiny corpus. Keep everything runnable on one machine.
17. Create a backend API for serving experiment results to internal users. It needs one report route, basic persistence, and a clear verification path. Start with the smallest credible slice.
18. I want a prompt-first repo for managing reusable prompt components and evaluation notes. It should be structured for assistant-led edits and human review checkpoints. Avoid unnecessary runtime code.
19. Build a service for tracking sync runs from external systems. The first version should record runs, expose a simple API, and include smoke plus integration tests. Keep infrastructure minimal.
20. Create a repo for comparing two storage backends against the same workload. I only need a small experiment harness and clear output summaries. Optimize for isolation and reproducibility.
21. I need a backend service for simple inventory snapshots. It should accept uploads, normalize records, and expose one reporting endpoint. Keep the repo aligned with assistant planning and verification.
22. Build a CLI that audits configuration files for policy violations. The first milestone is one command, fixture-based tests, and readable findings output. Keep the repo easy to extend later.
23. Create a local RAG repo for a policy handbook. It should index a fixed corpus and support deterministic query examples. The startup path should remain easy for a coding assistant to reason about.
24. I want a data pipeline that ingests JSON lines, validates them, and writes cleaned outputs. It should be deterministic and easy to inspect from tests. Start with one dataset.
25. Build a service for generating simple business KPIs from seed data. The first release needs a health route, one KPI endpoint, and a verification-friendly fixture set. Keep the repo compact.
26. Create a dokku-ready API for internal automation hooks. The first version should have one authenticated route and straightforward deployment notes. Prefer simple operational surfaces.
27. I need a repo for evaluating prompt variants against a small rubric. It should store prompts, fixtures, and evaluation results in a reviewable way. Keep the system prompt-first rather than app-heavy.
28. Build a Go service for parsing uploaded files and returning normalized summaries. The first milestone is one upload path, one summary route, and local tests. Keep the initial stack focused.
29. Create a Rust CLI for batch file classification. It should handle explicit commands, deterministic fixtures, and reliable output snapshots. The first plan should stay narrow and testable.
30. I want a backend for managing scheduled report runs. It should support one create flow, one list flow, and clear verification checkpoints. Keep the architecture simple enough for fast assistant execution.
31. Build a local search prototype for a folder of markdown docs. It should index a tiny sample set and support deterministic searches. Keep external services optional.
32. Create a repo for comparing raw and normalized records during ETL development. The first version should produce a readable diff artifact and include fixture-based verification. Optimize for inspection.
33. I need a service that receives webhooks and stores a normalized event log. The first milestone is one endpoint, one persistence boundary, and a smoke test. Keep operational complexity low.
34. Build a prompt-first knowledge repo for reusable assistant workflows. It should organize prompts, evaluation notes, and verification guidance. Avoid overbuilding runtime features.
35. Create a backend API for exposing precomputed customer metrics. It should start with one endpoint, one fixture dataset, and strong local tests. Bias toward a clean generated repo and plan-first execution.
36. I want a data pipeline repo for nightly enrichment jobs. The first cut needs one transformation path, deterministic inputs, and an easy validation story. Keep the repo disciplined and small.
37. Build a CLI that converts vendor exports into normalized CSV outputs. The initial scope is one command, one fixture set, and snapshot-friendly output. Keep onboarding simple for a coding assistant.
38. Create a local RAG repo for troubleshooting runbooks. It should emphasize deterministic corpora, local queries, and smoke checks. Avoid cloud dependencies in the first version.
39. I need an internal API for queue metrics and recent job summaries. The first milestone is a health route plus one metrics endpoint. Keep the surface minimal and verifiable.
40. Build a repo for testing multiple search backends against the same small corpus. I need clean comparisons, isolated configs, and clear result summaries. Start with the smallest experiment harness that works.
41. Create a backend service for storing and querying audit events. The first version should implement one write path, one read path, and local verification. Keep architecture choices explicit.
42. I want a prompt-first repo for managing system prompts, task prompts, and evaluation artifacts together. The repo should favor structure and reviewability over runtime code. Keep the workflow assistant-led.
43. Build a lightweight API that serves normalized summaries from a seeded dataset. The first release should stay narrow, include smoke tests, and have obvious next steps. Prefer a clean repo bootstrap.
44. Create a data pipeline for flattening nested partner payloads into tabular outputs. It should begin with one source format, deterministic fixtures, and strong validation. Keep transformations readable.
45. I need a CLI for replaying fixture events into a local service during testing. It should expose explicit commands and support predictable outputs. Keep the repo easy to verify end to end.
46. Build a Go or Python service for team dashboards backed by local seed data. The first slice is one route and one deterministic report. Keep the generated repo optimized for assistant execution.
47. Create a backend for normalizing and searching note snippets. The initial milestone is one ingest path, one search path, and local verification. Avoid unnecessary infrastructure.
48. I want a repo for comparing prompt outputs across model configurations. It should store inputs, outputs, and evaluation notes in a clear structure. Keep the first version prompt-first and reviewable.
49. Build a service that ingests status files and exposes current system summaries. The first release needs one ingest flow, one summary route, and a clean verification story. Keep the plan incremental.
50. Create a small project repo for an assistant-managed prototype where the human mainly validates direction and priorities. The assistant should derive the repo shape, propose the plan, and execute with checkpoints. Keep the bootstrap and verification paths explicit.

See `docs/usage/ADVANCED_ASSISTANT_OPERATIONS.md` for longer-lived sessions after the generated repo exists.
