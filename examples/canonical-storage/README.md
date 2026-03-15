# Canonical Storage Examples

Use this category for preferred patterns around databases, caches, queues, search systems, and vector stores.

## Examples in This Category

### Solo stack examples

- `mongo-weekly-reporting-example.md` — MongoDB collection bucketing, aggregation pipelines, partial indexes,
  and weekly retention via whole-collection drops. Use when the storage question is MongoDB-only.

- `redis-structures-example.md` — Redis native structures: sorted set (leaderboard), string-with-TTL
  (session/cache), hash (state record), stream (append log). Use when the storage question is Redis-only
  and the design choice is which structure fits the access pattern.

- `trino-federated-analytics-example.md` + `trino-federated-analytics-example.sql` — Federated analytics
  query joining a PostgreSQL catalog with a MongoDB catalog via Trino. Includes catalog configuration
  notes and a comparison against OLTP PostgreSQL use. Use when the query genuinely spans storage systems.

- `postgresql-query-shape-example.md` + `postgresql-query-shape-example.sql` — PostgreSQL DDL, partial
  indexes, bounded jsonb, reporting CTEs, and a materialized view pattern. Use when the storage question
  is transactional SQL or local analytical queries.

### Combined-stack examples
- `nats-jetstream-mongo-pipeline-example.md`
  Verification level: structure-verified
  Harness: none (follow-on: docker-compose with nats-server + mongo:7)
  Last verified by: verification/examples/data/test_storage_examples.py

- `duckdb-polars-example.md` + `duckdb-polars-example.py` — Local, embedded DuckDB used as a query engine with Polars as the output layer. Use when the data lives in a local DuckDB file under `docker/volumes/dev/` and the query result needs to be a Polars DataFrame. See the companion `.md` for the local-file vs S3 read-path distinction.

- `redis-mongo-shape-example.md` — Key-prefix and collection-naming conventions for repos that use Redis
  and MongoDB together. Use when the design question is how to isolate dev and test data across both
  systems simultaneously.

- `parquet-minio-example.md` + `parquet-minio-example.py` — Write a partitioned Parquet dataset to MinIO
  using PyArrow, then read it back with DuckDB. Covers schema pinning, Hive-style partition naming, the
  staging-prefix write pattern, and MinIO credential configuration. Use when the data-lake write path is
  the question.

- `nats-jetstream-mongo-pipeline-example.md` — Full capture-enrich-persist pipeline: producer publishes
  bounded request/response payloads to NATS JetStream; a separate consumer validates, cleans, enriches,
  and inserts to MongoDB. Covers ack-after-insert discipline, DLQ handling, enrichment field derivation,
  and weekly MongoDB collection bucketing. Use when the pipeline from event capture to reporting storage
  is the question.

## When To Use a Solo Example vs. the Combined Example

Use `redis-mongo-shape-example.md` when the repo uses Redis and MongoDB together and you need combined
isolation conventions in one place.

Use `redis-structures-example.md` when the workload is Redis-only and the question is which Redis
structure to use.

Use `mongo-weekly-reporting-example.md` when the workload is MongoDB-only and the question is collection
shape, index strategy, or aggregation pipelines.

Use the Trino example when the query spans multiple catalogs. Use the PostgreSQL example when the query
is local to a single PostgreSQL instance.

Use `parquet-minio-example.md` when the question is how to write Parquet files to an S3-compatible
store and make them readable by DuckDB or Polars.

Use `duckdb-polars-example.md` when the data lives in a local DuckDB file and the result needs to be
a Polars DataFrame. Do not use it as the S3 read path — for that, use `parquet-minio-example.py
read_back()`. When both the write path and the local analytical query layer are needed, load both
examples together; see the composition pattern in `duckdb-polars-example.md`.

Use `nats-jetstream-mongo-pipeline-example.md` when the question is how to capture events via NATS
JetStream, enrich them in a separate consumer process, and persist the enriched documents to a
weekly-bucketed MongoDB collection.

## Verification Metadata

- `parquet-minio-example.md`
  Verification level: structure-verified
  Harness: none (follow-on: minio_parquet_min_app scenario)
  Last verified by: verification/examples/data/test_storage_examples.py

- `parquet-minio-example.py`
  Verification level: structure-verified
  Harness: none (follow-on: minio_parquet_min_app scenario)
  Last verified by: verification/examples/data/test_storage_examples.py

- `nats-jetstream-mongo-pipeline-example.md`
  Verification level: structure-verified
  Harness: none (follow-on: docker-compose with nats-server + mongo:7)
  Last verified by: verification/examples/data/test_storage_examples.py

- `duckdb-polars-example.md`
  Verification level: structure-verified
  Harness: none
  Last verified by: verification/examples/data/test_storage_examples.py

- `duckdb-polars-example.py`
  Verification level: behavior-verified
  Harness: polars_data_pipeline
  Last verified by: verification/examples/python/test_polars_examples.py

- `redis-mongo-shape-example.md`
  Verification level: structure-verified
  Harness: none
  Last verified by: verification/examples/data/test_storage_examples.py

- `mongo-weekly-reporting-example.md`
  Verification level: structure-verified
  Harness: none
  Last verified by: verification/examples/data/test_storage_examples.py

- `redis-structures-example.md`
  Verification level: structure-verified
  Harness: none
  Last verified by: verification/examples/data/test_storage_examples.py

- `trino-federated-analytics-example.sql`
  Verification level: structure-verified
  Harness: none
  Last verified by: verification/examples/data/test_storage_examples.py

- `trino-federated-analytics-example.md`
  Verification level: structure-verified
  Harness: none
  Last verified by: verification/examples/data/test_storage_examples.py

- `postgresql-query-shape-example.sql`
  Verification level: structure-verified
  Harness: none
  Last verified by: verification/examples/data/test_storage_examples.py

- `postgresql-query-shape-example.md`
  Verification level: structure-verified
  Harness: none
  Last verified by: verification/examples/data/test_storage_examples.py

## A Strong Canonical Storage Example Should Show

- storage client or adapter boundary
- Docker-backed dev and test isolation
- one real write path and one real read or query path
- minimal integration-test structure against isolated test infrastructure
- any seed, fixture, or reset behavior needed for repeatability

## Choosing This Example

Choose this category when the main implementation question is about wiring a storage boundary correctly.

## Drift To Avoid

- storage logic demonstrated only through mocks
- examples that share dev and test data
- one huge multi-backend example that is hard to adapt safely
