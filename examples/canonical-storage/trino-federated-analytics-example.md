# Trino Federated Analytics Example

This example shows a federated query pattern that joins a PostgreSQL catalog with a MongoDB catalog
inside a single Trino query.

## When Trino Is the Right Tool

Use Trino when:

- the question spans data in two or more storage systems
- the query is analytical and read-only (aggregations, rollups, reports)
- neither source system should bear the cross-system join cost

Do not use Trino for:

- OLTP writes or row-by-row transactional reads
- latency-sensitive paths where a sub-millisecond response is expected
- queries where pushdown cannot eliminate most of the scan (see pushdown notes below)

## Catalog Configuration

Both source catalogs must be registered in Trino's `etc/catalog/` directory before queries run.

Example `etc/catalog/postgresql_prod.properties`:

```properties
connector.name=postgresql
connection-url=jdbc:postgresql://postgres:5432/mydb
connection-user=trino_read
connection-password=${ENV:TRINO_PG_PASSWORD}
```

Example `etc/catalog/mongo_events.properties`:

```properties
connector.name=mongodb
mongodb.connection-url=mongodb://mongo:27017
```

Schema emulation (inferring column types from document fields) is the default behaviour in Trino 448+.
Earlier versions required `mongodb.schema-emulation.enabled=true`; that property was removed when
emulation became unconditional.

These catalog names (`postgresql_prod`, `mongo_events`) must match the catalog-qualified table names
used in the SQL.

## Catalog-Qualified Table Names

Every table reference in a cross-catalog query must be fully qualified as `catalog.schema.table`:

```sql
postgresql_prod.public.tenants
mongo_events.reporting.request_logs
```

Omitting the catalog prefix causes Trino to look in the session default catalog, which will not have
the cross-catalog tables and returns a misleading "table not found" error.

## Cross-Catalog Join Pattern

The companion SQL file is `trino-federated-analytics-example.sql`.

The join key (`tenant_id`) must exist in both sources. Trino executes the join on the coordinator
after fetching rows from each connector. For large result sets this means data is transferred to the
coordinator before the join runs. Keep the `WHERE` clause tight to minimise connector scan size.

## Pushdown Caveats

Trino attempts to push `WHERE` clauses into each connector, but:

- MongoDB connector pushdown support varies by filter type and Trino version
- Complex expressions or casts may cause a full collection scan on the MongoDB side
- Always `EXPLAIN` the query and check for a `TableScanNode` without a filter push

If pushdown is not occurring on the time filter, consider pre-aggregating in MongoDB first or staging
a view that narrows the scan window.

## Trino vs. PostgreSQL for Analytics

| Concern | Trino | PostgreSQL |
|---|---|---|
| Cross-source joins | Native | Requires foreign data wrapper (FDW) |
| OLTP writes | Not supported | Supported |
| Latency | Seconds to minutes | Sub-second for indexed reads |
| Large distributed scans | Horizontal, multi-node | Single-node, vertical |
| Schema authority | External catalogs | Internal DDL |

Use PostgreSQL for transactional workloads and analytical queries on local data. Use Trino when the
query genuinely spans storage boundaries and the latency trade-off is acceptable.

## Verification Level

Structure-verified (file existence and SQL marker checks only). No live Trino federation harness is
wired in the default verification tier. Federation behaviour depends on connector versions and catalog
configuration that are environment-specific.
