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
python scripts/new_repo.py --list-examples
python scripts/new_repo.py --list-derived
python scripts/new_repo.py --use-example 1 --dry-run --target-dir /tmp/example-001
python scripts/new_repo.py --derived-example ingestion-normalization-core
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
- renders `AGENT.md`, `CLAUDE.md`, `.gitignore`, and generated profile files
- defers a substantial root `README.md` and root `docs/` by default unless you explicitly ask for them or a narrowly scoped operational need requires them
- optionally renders prompt files, seed data, smoke tests, integration tests, and Dokku assets
- generates isolated `docker-compose.yml` and `docker-compose.test.yml` when the profile implies local infra

## Documentation Timing For Derived Repos

In a fresh derived repo, root `README.md` and root `docs/` often become stale faster than the implementation because they are written before the repo has enough real structure. The default posture is therefore:

- let `AGENT.md`, `CLAUDE.md`, and the generated profile carry early boot guidance
- add front-facing root docs only after the implementation has a meaningful slice to describe honestly
- allow narrowly scoped operational docs when they are explicitly needed

If you truly want early front docs anyway, use the generator flags that opt into them intentionally instead of treating them as mandatory boilerplate.

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
- avoid eager front-facing README and docs content that describes architecture the repo has not implemented yet

## Using a Reference Example

`new_repo.py` ships with a catalog of 100 reference projects covering every
supported archetype and stack combination.  Each entry has a short codename,
an archetype, a primary stack, and a set of boolean flags (dokku,
smoke-tests, integration-tests, seed-data).

**Browse the catalog:**

```bash
python scripts/new_repo.py --list-examples
```

**Bootstrap directly from a catalog entry:**

```bash
# Pre-fills archetype, stack, and flags from project #1.
# repo_name defaults to 001-partner-data-enrichment.
python scripts/new_repo.py --use-example 1 --target-dir /tmp/001-partner-data-enrichment

# Preview what would be generated without writing files.
python scripts/new_repo.py --use-example 47 --dry-run --target-dir /tmp/047-go-python-ml-gateway
```

**Override any pre-filled value:**

Explicit flags always win over catalog defaults.  Pass any supported flag
to override the pre-filled value:

```bash
# Use project #12 but give it a custom repo name.
python scripts/new_repo.py my-scheduler --use-example 12 --target-dir /tmp/my-scheduler

# Use project #91 but skip seed data.
# Note: --use-example pre-fills smoke-tests and seed-data from the entry,
# but there is no --no-seed-data flag; omit seed data by not passing the flag
# and letting the example's seed_data=True take effect (or choose a different entry).
python scripts/new_repo.py --use-example 91 --dry-run --target-dir /tmp/091-dokku-fastapi
```

**Preview with `--dry-run`:**

Use `--dry-run` to see the planned file list before generating anything:

```bash
python scripts/new_repo.py --use-example 20 --dry-run --target-dir /tmp/020-crystal-cache-proxy
```

## 100 Example Initial Prompts

Use these as starting points inside `agent-context-base`. Each prompt is 2–4 sentences and references a specific stack, pattern, or capability from this base rather than describing a vague service. Adjust domain details, constraints, and deployment expectations, then let the assistant translate the prompt into `new_repo.py` arguments.

---

### Category A — Single-Backend API Services

1. Build a FastAPI partner data enrichment service that accepts JSON payloads, normalizes them with Polars, and stores results in PostgreSQL with a filtered search endpoint using cursor-based pagination. The first milestone is one write path, one query endpoint, and integration tests against a real PostgreSQL container.

2. I need a FastAPI analytics API that queries DuckDB over Parquet files, applies Polars transforms, and serves paginated aggregate results from two endpoints: one summary and one time-bucketed trend. Smoke tests should run against a fixture Parquet file with no live dependencies.

3. Create a FastAPI time-series ingestion service backed by TimescaleDB that accepts timestamped metric events, writes to a hypertable, and serves windowed aggregate queries. Use uv tooling, explicit schemas, and a docker-compose.yml with isolated TimescaleDB.

4. Build a FastAPI webhook receiver that rate-limits inbound events using Redis, stores normalized event documents in MongoDB with Polars transforms, and exposes a recent-events list endpoint. Start with one event type, deterministic fixtures, and smoke tests.

5. I need a FastAPI scheduled enrichment service that runs a nightly job against PostgreSQL, applies Polars transformations to flag stale records, and exposes one inspection endpoint showing the last enrichment run state. Keep the first version one job, one route, and fixture-driven.

6. Build a lightweight Hono/Bun internal API with three endpoints: a health check, a configuration-read route, and one domain-specific query backed by a local SQLite file. Keep startup fast and the first implementation test-covered and narrow.

7. Create a Hono/Bun backend-for-frontend service that aggregates two upstream REST APIs and serves a unified JSON response for a dashboard client. The BFF should handle upstream failures gracefully and return partial data with explicit error fields — make it Dokku-ready from the start.

8. I need a Go/Echo reporting service that reads precomputed Parquet files, applies filter and sort logic, and returns paginated JSON results. The first milestone is one endpoint, file-backed storage, deterministic smoke tests, and no external dependencies.

9. Build a Go/Echo service for receiving uploaded files, running validation and normalization, and storing processed records in PostgreSQL. Cover one file type, one write path, one status-check route, and an explicit docker-compose.yml isolation layout.

10. Create a Rust/Axum service for high-throughput event ingestion that buffers inbound events and batch-flushes to a PostgreSQL append table. Verification should prove the write path and a minimal flush cycle against a real database container.

11. Build a Rust/Axum batch classification service that accepts arrays of feature vectors, runs a classification function, and returns labeled results with confidence scores. The first implementation covers the classification boundary, response shape, and a unit test harness — no over-engineering of the inference layer.

12. I need an Elixir/Phoenix backend for a scheduling and availability service that accepts availability windows, computes overlapping slots, and exposes a JSON API backed by PostgreSQL with Ecto. The first milestone is one write path, one query path, and smoke tests.

13. Build a Scala/Tapir/ZIO API for a financial report aggregation service with two endpoints: one fetching period summaries and one comparing two periods. Use ZIO for effect management and Tapir for typed route definitions; keep the first milestone narrow and verifiable.

14. Create a Kotlin/http4k/Exposed service for tracking supplier invoice records with basic CRUD and a filter-by-status endpoint backed by PostgreSQL. Structure the repo for assistant-led development with explicit verification steps at each slice.

15. Build a Clojure/Kit backend for a user preference service that accepts updates, stores them in PostgreSQL via next.jdbc, and returns current preference state. One write endpoint and one read endpoint — keep the architecture small and fixture-verifiable.

16. I need a Ruby/Hanami API for a lightweight content record store that accepts submissions, stores them in PostgreSQL, and exposes a paginated list endpoint with basic filtering. Keep the implementation Hanami-conventions-first and smoke-tested.

17. Create a Nim/Jester API that reads fixture JSON files, filters by query params, and returns structured responses. The first milestone is one endpoint, deterministic fixtures, and syntax-checked implementation — no live storage in v1.

18. Build a Dart/Dartfrog internal audit log service that accepts log entries, stores them in PostgreSQL, and serves a paginated audit trail endpoint. Cover the write path, the read path, and a minimal boot check in the first implementation slice.

19. I need an OCaml/Dream service backed by Caqti and PostgreSQL for a project metadata store supporting record creation and lookup, with Tyxml for any HTML fragment responses. Two endpoints, one table, structural verification — keep scope narrow.

20. Build a Crystal/Kemal API proxying service that caches responses by key in PostgreSQL via Avram and exposes a cache-stats endpoint. The first plan is one proxy target, one cache key scheme, and smoke tests.

21. Create a FastAPI analytics service deployable to Dokku that normalizes CSV exports with Polars, writes to PostgreSQL, and includes docker-compose.yml for local dev, docker-compose.test.yml for integration tests, and Dokku deployment notes. First slice: one ingest endpoint and one summary query.

---

### Category B — Backend-Driven UI with HTMX + Tailwind + Plotly

22. Build a FastAPI + HTMX + Tailwind analytics dashboard with a faceted include/exclude filter panel, dynamic result counts that update as filters change, and a Plotly chart tied to the same filtered query state. Use Playwright to verify that filter changes produce correct fragment updates and exact counts.

23. Create a backend-driven search and sort UI using FastAPI, HTMX, and Tailwind where users can search by keyword, sort by one of three fields, and scroll through paginated results via HTMX fragment swaps. Cover the search → sort → scroll sequence with a Playwright test that verifies correct result ordering.

24. Build a FastAPI + HTMX interface with a split filter panel — left side shows include-selectable facets, right side shows an active exclude strip — where filter state is maintained server-side and reflected exactly in result counts. Playwright should verify that excluding a facet removes matching records and updates counts precisely.

25. I need a FastAPI data view where a Plotly chart and a result table share one backend query: the same filters limit both the table and the chart data. Use HTMX to replace the result fragment and chart payload on each filter change, and add a Playwright test confirming they reflect the same filtered record set.

26. Create a FastAPI report browser with an HTMX + Tailwind interface covering these critical user journeys: load the report list, apply a filter, sort by date, inspect a single report detail, and export a filtered result set. Write Playwright CUJ tests for each journey — the emphasis is on backend correctness and test coverage, not UI polish.

27. Build a FastAPI + HTMX dashboard with compound facet state where multiple filter dimensions (category, date range, status) combine with AND logic on the backend. Facet counts must reflect the intersection of all active filters. Include Playwright tests that verify count correctness under multi-dimension filter combinations.

---

### Category C — Data Acquisition and Pipelines

28. Build a Python data acquisition service that pulls records from a paginated REST API, respects rate limits with explicit backoff, archives raw JSON payloads to disk, and tracks sync state in PostgreSQL. The first milestone covers one source endpoint, the archive step, and a local replay test against fixture payloads.

29. I need a Go-based API ingestion service that fetches daily data from an external JSON API, archives raw downloads, parses records into a normalized schema, writes results to PostgreSQL, and implements exponential backoff on failures. Include structured logging and an explicit docker-compose.yml.

30. Create a Python scraping service that extracts structured records from a static HTML source, normalizes them with Polars, archives raw HTML per run, and stores clean records in PostgreSQL. Focus the first plan on one source structure and explicit parser tests against small fixture HTML files.

31. Build a TypeScript/Bun scraping service that fetches and parses structured HTML, archives raw pages, and writes normalized records to PostgreSQL via Drizzle. Emphasize deterministic fixture-based tests for the parser and normalization steps.

32. I need a Python ETL pipeline that reads multiple input CSV formats, applies Polars transforms to normalize and join them, and writes clean Parquet outputs. The first milestone is one source format, one transform path, and deterministic output verification using small fixture files.

33. Build a Python ETL pipeline using Polars that reads partner JSON exports, validates and enriches records, and bulk-inserts results into a PostgreSQL staging table. Include a fixture-based test that runs the full transform path against sample inputs and asserts row counts and selected field values.

34. Create a local analytical pipeline using DuckDB and Parquet — ingest CSV files, write them to Parquet, and expose analytical queries via DuckDB SQL. The first milestone is one data domain, one transform script, and deterministic query outputs verified against fixture Parquet files with no cloud dependencies.

35. Build a Python multi-source sync platform that coordinates pulls from two external sources using a NATS JetStream event bus. Source adapters publish sync events; a coordinator subscribes and triggers downstream processing. Cover two sources, one event contract, and a local integration test.

36. I need a Python service that reads normalized records from PostgreSQL, applies a classification function, writes enriched records back with a classification tag and confidence score, and logs provenance. The first milestone is one record type, one classifier, and fixture-based verification.

37. Build a Python recurring sync service for a time-sensitive external data feed with configurable schedule, exponential backoff with jitter, raw payload archival, and sync run metadata in PostgreSQL. First plan: one source, one complete run cycle, explicit retry logic tests.

38. Create an Elixir data acquisition service using GenServer scheduling that polls a paginated REST API, archives raw JSON payloads, normalizes records with Ecto schemas, and stores results in PostgreSQL with explicit backoff. First milestone: one source, one complete poll cycle, fixture-based verification.

---

### Category D — ML and Data Science

39. Build a FastAPI inference service for a scikit-learn classification model that accepts feature vectors, runs inference, and returns class probabilities from a persisted model artifact loaded at startup. Include a health endpoint, a predict endpoint, and smoke tests against a fixture model file.

40. I need a FastAPI recommendation endpoint backed by a Polars data layer that accepts a user ID, queries a precomputed recommendation table from PostgreSQL, and returns a ranked list of recommended items. Focus on the query path, the ranking transform, and an explicit data fixture.

41. Create a FastAPI time series forecasting service that fits an ARIMA model using statsmodels on a given input series and returns a multi-step forecast with confidence intervals and fitted parameters. First milestone: one time series domain, fixture data, deterministic output verification.

42. Build a FastAPI semantic search service that embeds text queries with sentence-transformers and retrieves similar documents from a Qdrant collection. Support collection initialization from a fixture corpus and a query endpoint returning ranked results with scores — include a smoke test that indexes a tiny corpus.

43. I need a FastAPI API for a gradient-boosted tabular model trained with XGBoost that loads a persisted model, accepts structured feature inputs, and returns predictions with feature importance metadata. Include a fixture model file and a smoke test verifying the predict endpoint returns expected classes.

44. Build a Python embedding pipeline that generates embeddings from a document set using sentence-transformers, stores them in Qdrant with structured metadata, and exposes a similarity query endpoint via FastAPI. Cover document ingestion, embedding generation, Qdrant upsert, and a query path with a small deterministic fixture corpus.

45. Create a Python data science pipeline repo using DuckDB, Polars, and scikit-learn: load Parquet files into DuckDB, transform feature sets with Polars, train a classification model, and output evaluation metrics. Structure it for notebook-to-script promotion with explicit fixture data — this is a research pipeline, not a web service.

46. Build a Python LightGBM tabular modeling pipeline that reads training data from Parquet, applies Polars feature engineering transforms, trains a model, and produces a classification report. Include a small fixture dataset and deterministic evaluation output — expose results as CLI output or Jupyter-compatible artifacts.

---

### Category E — Multi-Backend Coordination

47. Build a Go/Echo gateway service and a FastAPI Python ML scoring service communicating over a REST seam. The Go service receives client requests, calls the Python scoring endpoint with normalized features, and returns the scored result. Show the seam layer explicitly and verify end-to-end with docker-compose.

48. Create a Kotlin/http4k caller and a Rust/Tonic gRPC compute server where Kotlin sends computation requests to the Rust kernel and logs duration and method. The seam is defined in a .proto file shared by both sides — verify end-to-end with docker-compose.

49. Build an Elixir publisher and a Go NATS JetStream consumer for an event fan-out use case. The Elixir service publishes domain events to a NATS subject; the Go service subscribes, decodes, and logs received events. Demonstrate subject structure, message schema, and consumer acknowledgment.

50. I need a Clojure Kafka producer and a Go Kafka consumer for domain event enrichment. Clojure produces enrichment events with a correlation ID; Go consumes, applies a transformation, and logs the enriched result. Show topic config, message format, and Kafka broker coordination via docker-compose.

51. Build a Node/Hono GraphQL BFF that resolves queries by calling a Go/Echo domain API over REST. The GraphQL schema exposes one query type that the BFF resolves by calling Go — show the GraphQL resolver, HTTP client call, and response mapping. Verify with docker-compose.

52. Create a Scala/Akka Streams pipeline that delegates compute steps to a Rust/Tonic gRPC kernel. Scala streams records through a pipeline stage that calls Rust for a compute-intensive step and collects results. Show the proto definition, Akka gRPC client, and Rust server via docker-compose (first build takes several minutes).

53. Build a Node service that publishes client action events to NATS and an Elixir service that consumes them, updates distributed state, and rebroadcasts results. Show the bidirectional NATS seam: Node publish, Elixir subscribe and process, Elixir publish, Node receive — verify end-to-end with docker-compose.

54. I need a Rust/Tonic gRPC inference server and a Python orchestrator that batches feature inputs, calls the Rust inference RPC, and collects predictions. Show the proto definition, Rust handler, Python gRPC client, and response handling — verify with docker-compose (note: several-minute Rust compile).

55. Create an Elixir service that loads a Rust compute kernel as a NIF using Rustler. The Rust NIF exposes one pure compute function callable from Elixir with zero network overhead. Show the mix.exs + Rustler config, NIF module, and an Elixir integration test — no docker-compose, this is an in-process seam.

56. Build an Elixir RabbitMQ producer and a Clojure Broadway consumer for a work queue. Elixir publishes work items; Clojure consumes via Broadway and processes each item. Show exchange config, routing key, Broadway pipeline, and acknowledgment behavior — verify with docker-compose + RabbitMQ.

57. Build a three-service system: a Go gateway publishes jobs to NATS JetStream, an Elixir coordinator subscribes and orchestrates, and a Python service performs ML scoring via REST. Show all three seam layers — Go → NATS → Elixir and Elixir → REST → Python — in one docker-compose.

58. Create a Go gateway that calls a Rust compute kernel via gRPC, then calls a Python scoring service via REST, combining both results. Show both seam types in one docker-compose: Go → gRPC → Rust and Go → REST → Python. First build takes several minutes due to Rust compile.

59. Build an Elixir coordinator that publishes tasks to NATS JetStream, a Go worker that subscribes and calls a Rust kernel via gRPC, and publishes completion events back to Elixir. Show supervision and fault tolerance on the Elixir side and verify the full round-trip with docker-compose.

60. Create a Node GraphQL BFF that resolves user recommendation queries by calling a Go domain service (REST) for user data and a Python ML service (REST) for recommendations. Show both resolution paths in one docker-compose and demonstrate GraphQL schema stitching with downstream REST calls.

61. Build a real-time IoT event pipeline: Rust ingestor receives high-throughput events, publishes to NATS JetStream, Go worker subscribes for windowed aggregation, and exposes aggregates via a Go REST endpoint. Verify with docker-compose and a fixture event stream.

62. I need a Scala service that queries a Go analytics worker via gRPC for pre-aggregated metrics and combines results with a Python data layer (REST) for a federated analytics use case. Show the seam contracts where each backend owns its data domain and verify the full federation path with docker-compose.

---

### Category F — Storage-Focused Experiments and Infra

63. Create a local data lake experiment using DuckDB, Parquet, and MinIO. Include scripts to upload Parquet files to MinIO, query them via DuckDB's S3-compatible extension, and return aggregated results. One dataset, one upload script, one query, and a docker-compose.yml with isolated MinIO.

64. Build a local RAG system for engineering runbook documents — index a deterministic fixture corpus in Qdrant using sentence-transformers, implement a query endpoint returning ranked documents with scores, and add a smoke test against the fixture corpus. No cloud dependencies.

65. I need a FastAPI service with Meilisearch as the search backend that indexes structured document records, exposes a full-text search endpoint, and supports field-level attribute ranking and filtering. Include fixture data, docker-compose.yml with Meilisearch, and smoke tests verifying index setup and search result correctness.

66. Build a FastAPI analytics service backed by TimescaleDB that ingests timestamped sensor readings into a hypertable and exposes windowed aggregate endpoints — hourly averages and daily totals. Verify with integration tests that write fixture data and assert aggregate values against a real TimescaleDB container.

67. Create a FastAPI service with a Redis caching layer for expensive query results and a Redis-based rate limiter for API endpoints. One cached endpoint, one rate-limited endpoint, and integration tests using a real Redis container that verify cache hit/miss behavior and rate-limit rejection.

68. Build a NATS JetStream event capture and replay experiment. One service publishes structured events to a JetStream stream with retention policy; a replay script re-reads from a specific sequence. Show stream config, publish, subscribe, and replay patterns in a docker-compose that includes NATS JetStream.

69. I need a Trino federated query experiment that configures two Trino catalogs (PostgreSQL and Parquet via filesystem connector), exposes one cross-catalog query via a FastAPI endpoint, and verifies correct results from both sources. Use docker-compose for the full Trino stack.

70. Build a multi-storage experiment combining Redis (hot cache and recent-events list), MongoDB (durable document retention with aggregation pipelines), and Parquet (batch export output). Show a realistic read/write split and verify each storage boundary independently.

71. I need an Elasticsearch-backed search experiment using FastAPI that indexes a domain-specific document corpus, exposes a search endpoint with relevance scoring and field filtering, and supports index update operations. Include fixture data, docker-compose.yml with Elasticsearch, and smoke tests for the index-and-query path.

72. Build a search backend comparison repo that indexes the same document corpus in both Elasticsearch and Meilisearch and exposes a side-by-side query endpoint for each backend. The repo should produce comparable relevance results and timing metadata from both systems, running both backends in docker-compose isolation.

---

### Category G — CLI Tools

73. Build a Python CLI for reconciling two data source exports — the tool accepts two file paths, compares records by key, and produces a structured diff report showing matched, unmatched, and conflicting records. One record type, one comparison mode, and fixture-based tests for the first milestone.

74. I need a Python CLI for evaluating prompt variants against a small fixture dataset. The CLI accepts a prompt file and a fixture file, runs each variant, and produces a structured comparison report. Keep the repo prompt-first with deterministic fixture handling and clear eval output.

75. Create a Rust CLI for batch processing structured input files: accept a directory of inputs, apply validation and normalization to each, and write clean outputs with a processing report. One input format, one output format, and deterministic snapshot tests for the first version.

76. Build a Rust CLI tool where output snapshot tests are the primary verification discipline. The CLI produces structured JSON output for a specific data processing task; snapshot tests verify exact output for a set of fixture inputs. Keep the implementation minimal and the snapshot harness explicit.

77. I need a Go CLI for auditing configuration files against a policy rule set. The CLI reads configurations from a directory, applies rules defined in a YAML policy file, and outputs a structured findings report. Two rules, two fixture configs, and explicit pass/fail output for the first milestone.

78. Build a Python CLI that wraps a data acquisition and normalization pipeline, exposing subcommands for triggering a sync, inspecting the last sync state, and running a fixture replay. Keep the CLI as a thin coordination layer over the pipeline logic — one data source and explicit sync state tracking.

---

### Category H — Local RAG and Semantic Search

79. Build a local RAG system for a private legal document corpus. Index a deterministic fixture corpus in Qdrant using sentence-transformers, expose a FastAPI query endpoint returning semantically matched excerpts with metadata, and add smoke tests that verify non-empty results for representative queries.

80. I need a local RAG system for searching API reference documentation. Index structured API docs as chunks in Qdrant with metadata (endpoint, method, description), support semantic query, and return ranked results with exact metadata fields. Use a deterministic fixture corpus.

81. Create a local engineering notes indexer that processes a folder of Markdown files, chunks them by section, embeds each chunk with sentence-transformers, and stores chunks in Qdrant with source file and section metadata. The query endpoint returns the most relevant chunk and its source — keep the corpus deterministic for smoke tests.

82. Build a policy and runbook search system using FastAPI and Qdrant that indexes operational runbooks as searchable chunks, supports query by intent, and returns the most relevant runbook step with context. Include a small fixture runbook set and a smoke test.

83. I need a hybrid search prototype combining Meilisearch full-text search and Qdrant semantic search for the same document corpus. The FastAPI endpoint runs both queries in parallel, merges results by weighted rank fusion, and returns a unified ranked list. Verify that result ordering is deterministic for fixture queries.

84. Build a FastAPI service where a RAG retrieval step supplements structured query results — for a given query, retrieve semantically similar context documents from Qdrant, use them to enrich a structured result, and return both the structured result and the source context chunks. Use a deterministic fixture corpus for smoke tests.

---

### Category I — Prompt-First Repos

85. Build a prompt-first repo for managing and evaluating system prompts against a structured rubric defined as a YAML file. The repo organizes prompt files monotonically, applies the rubric to prompt outputs, and produces scored evaluation reports. Keep the repo light on runtime code and heavy on verifiable structure.

86. I need a prompt-first repo that evaluates prompts specifically on output shape compliance. Each prompt defines an expected JSON schema; the evaluation harness checks whether model outputs conform. First milestone: one prompt family, two variants, and a fixture-based shape compliance check.

87. Create a prompt-first system prompt library where each prompt is accompanied by a set of expected output assertions that verify key properties of model responses. The library structure should be monotonic, reviewable, and verifiable by a single harness run.

88. Build a prompt-first repo for comparing model outputs across Claude configurations. The harness accepts a prompt set, runs each against two or more model configs, and produces a structured comparison report with output length, compliance score, and key phrase presence. Keep the harness decoupled from any specific application.

89. I need a prompt-first repo that generates task-specific prompt sequences for a defined domain. Each sequence is monotonically numbered, references specific output shapes and continuation conditions, and is evaluable by the existing harness. Start with one domain and three sequence steps.

90. Build a prompt-first repo that doubles as a living documentation base. Prompts generate documentation fragments for a defined technical domain; the verification harness checks that generated fragments meet structure and length constraints. The repo should be usable by assistants as a knowledge-generation and documentation-maintenance tool.

---

### Category J — Dokku-Deployable Services

91. Build a FastAPI analytics service deployable to Dokku with one aggregate query endpoint backed by PostgreSQL, a Procfile, app.json, and environment variables for all secrets. Include docker-compose.yml for local dev, docker-compose.test.yml for integration tests, and a Dokku deployment checklist.

92. I need a FastAPI caching service that uses Redis for result caching and is deployable to Dokku. Include the Procfile, Dokku Redis plugin configuration notes, and environment variable discipline for all Redis credentials. One cacheable endpoint with explicit cache-miss and cache-hit paths verified locally.

93. Build a Hono/Bun API service deployable to Dokku with a health check endpoint and one domain-specific query. Include a Procfile, Dokku-compatible runtime config, and an explicit environment variable map — keep it narrow and deployable from the start.

94. Create a Go/Echo service backed by PostgreSQL and deployable to Dokku. One health endpoint and one reporting route, with a Procfile, go.mod, and a Dokku deployment checklist. Structure the repo for assistant-led development with explicit verification checkpoints.

95. Build an Elixir/Phoenix application deployable to Dokku with one API route and one server-rendered view. Include the Procfile, elixir_buildpack.config, and PostgreSQL integration via Ecto. First milestone: one table, one route, one Dokku-compatible release step.

96. I need a multi-service Dokku application where a FastAPI backend and a Hono/Bun BFF are deployed as separate Dokku apps sharing a PostgreSQL database. Show service isolation, shared environment variables, and the coordination contract between the two services. Include Dokku deployment notes for each.

97. Build a Rust/Axum API service deployable to Dokku with one health endpoint and one domain-specific route. Include a Procfile, Docker build stage, and explicit environment variable config — note that first deploy will take several minutes due to Rust compile time.

98. Create a Kotlin/http4k service deployable to Dokku with one reporting route backed by PostgreSQL, a Procfile, JVM startup config, and a Dokku deployment checklist. Structure the repo for assistant-led development with incremental verification.

---

### Additional Prompts

99. Build a Crystal/Kemal data acquisition service that fetches structured records from an external API, validates them against an expected schema, archives raw payloads, and stores normalized results in PostgreSQL via Avram. One source, one schema, smoke-tested against a fixture response file.

100. Create a polyglot lab repo for experimenting with a seam pattern between two or three languages not yet covered in the canonical multi-backend examples. Set up the coordination infrastructure (broker or REST seam), define a minimal message contract, and demonstrate one end-to-end round trip. Use docker-compose for isolation and include explicit notes on what the experiment discovered.

---

See `docs/usage/ADVANCED_ASSISTANT_OPERATIONS.md` for longer-lived sessions after the generated repo exists.
