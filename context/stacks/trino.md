# Trino

Use this pack when a repo uses Trino as a federated analytics query layer over multiple data sources. Trino is the right choice for cross-source analytical queries, warehouse-style read paths, and analytical rollups that should not run on OLTP traffic. It is not a transactional database and is not appropriate for writes, low-latency lookups, or point queries on a single source.

When a repo uses two or more distinct storage systems and there is a meaningful analytical overlay across them, Trino should be considered as the federated query fabric. Load this pack alongside the storage packs for those sources.

Poor fit: operational queries with < 100ms latency budgets, any write path, or repos with a single well-defined data source that can be queried directly.

## Typical Repo Surface

- `etc/catalog/*.properties` — Trino catalog configuration files, one per connected source
- `app/queries/*.sql` or `app/queries/*.py` — analytical query modules
- `docker-compose.yml` — Trino coordinator container plus backing source containers
- `tests/integration/test_trino_*.py` — integration tests against a real Trino instance
- `scripts/seed_data.py` — seeds fixture data into the connected sources before query tests run

## Compatible Catalogs

Not every storage system belongs behind Trino. Add a catalog when it materially improves cross-source analytics:

- **PostgreSQL** — via `postgresql` connector; analytical queries and reporting views across a relational source
- **MySQL / MariaDB** — via `mysql` connector
- **Hive / S3 / object storage** — via `hive` or `iceberg` connector; suited to large-scale scan workloads
- **MongoDB** — via `mongodb` connector; limited pushdown; better suited to lookup-style joins than aggregations
- **Kafka** — via `kafka` connector; streaming data exposed as a queryable table surface

Do not add a catalog unless the repo genuinely runs cross-source queries. A single-source repo using Trino is almost always better served by querying that source directly.

## Kafka Connector Depth

This section gives operational detail on the Kafka catalog. For the full combo pattern (Kafka topics as Trino-queryable tables, cross-source joins, topic table definition files), see `context/stacks/kafka-trino.md`.

Key operational notes:

- The Kafka connector reads topic messages at query time (not indexed) — queries scan all partitions. Use `LIMIT` aggressively in dev/test to avoid long-running scans.
- Topic table definition files (`.json`) must live in the directory pointed to by the Trino server config's `kafka.table-description-dir` property. Mount this directory as a volume in docker-compose.
- The connector supports JSON, CSV, and Avro (with Confluent Schema Registry) decoders. Set `"dataFormat": "json"` in the table definition for JSON-encoded topics.
- The `_partition_offset` and `_timestamp` built-in columns are useful for bounding scans. Add `WHERE _timestamp > TIMESTAMP '...'` to limit scan scope in larger topics.
- Prefer the bitnami/kafka KRaft single-container setup for local dev. The confluentinc/cp-kafka + ZooKeeper stack is only needed when a Confluent Schema Registry is also required alongside Trino.

## Change Surfaces To Watch

- **Catalog config** (`etc/catalog/*.properties`): connector name, connection URL, authentication. Changes here break the entire catalog, not just one query.
- **Type mismatches**: Trino type inference across connectors is imperfect. Explicit casts are often required when joining across catalogs with different type representations.
- **Pushdown assumptions**: filter and aggregation pushdown behavior varies by connector. A query that runs efficiently with pushdown enabled may scan the entire source without it. Verify with `EXPLAIN` before assuming performance characteristics.
- **Query cost**: Trino is designed for scans, not point lookups. Large cross-source joins can be expensive. Size fixture datasets in tests to reflect realistic selectivity, not just functional correctness.
- **Worker topology**: single-node Trino (coordinator only) is fine for development and testing. Be explicit about coordinator-only versus worker separation if the repo targets a real cluster.

## Testing Expectations

- Run integration tests against a real Trino instance (Docker-backed coordinator)
- Prove one cross-catalog query with at least two connected sources
- Prove filter pushdown behavior if it is a correctness concern for the query
- Keep fixture datasets in connected sources tiny — Trino query tests fail loudly on connectivity and type issues, not dataset size
- Do not mock Trino query execution — connector behavior is the thing being tested

## Trino-Shaped Queries

Queries that fit Trino well:

- Cross-catalog join: `SELECT * FROM postgresql.analytics.events e JOIN mongo.logs.requests r ON e.request_id = r.id`
- Multi-source rollup: aggregate counts from three separate databases in one query
- Warehouse read path: large analytical aggregation over historical data that should not touch the OLTP primary
- Federated audit query: pull matching records from two separate systems into one result set

Queries that are not Trino-shaped:

- Single-source point lookup by primary key
- Any write operation
- Low-latency request path

## Common Assistant Mistakes

- Treating Trino as a general-purpose database and routing OLTP traffic through it
- Adding a catalog for a data source that is never joined with another catalog in the repo
- Assuming all connectors support the same SQL dialect — Trino SQL is ANSI-ish but each connector has limitations and omissions
- Forgetting that Trino does not handle writes — any write path must go directly to the backing source
- Missing `EXPLAIN` verification for queries that depend on pushdown for acceptable performance
- Not accounting for type coercion when joining across catalogs with different type representations (e.g., `varchar` versus `text`, integer widths)

## Related

- `context/stacks/kafka-trino.md` — Kafka as a Trino-queryable data source (full combo pattern)
- `context/stacks/kafka.md` — Kafka stack doc (producer/consumer patterns, KRaft setup)
- `context/stacks/duckdb-trino-polars.md` — DuckDB + Trino + Polars combo pack
