# TimescaleDB

Use this pack when the repo stores time-series analytics in PostgreSQL with TimescaleDB features.

## Typical Repo Surface

- schema and migration files
- query modules for rollups or windows
- ingestion jobs
- retention or compression settings

## Change Surfaces To Watch

- hypertable creation
- retention policies
- write path shape
- aggregation queries

## Testing Expectations

- run real integration tests against a TimescaleDB-enabled test instance
- prove one write path and one representative aggregate query
- add an edge case around time windows or empty-series behavior when relevant

## Common Assistant Mistakes

- treating TimescaleDB like plain PostgreSQL everywhere
- skipping migration verification
- testing only query builders and not actual SQL behavior

