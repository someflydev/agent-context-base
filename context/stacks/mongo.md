# MongoDB

Use this pack when a repo uses MongoDB as its primary operational datastore, reporting store, or log archive. MongoDB earns its place when document shape varies meaningfully between record types, when retention is managed by dropping whole collections, or when aggregation pipelines are the primary reporting path.

Poor fit: repos that need multi-table joins, strong transactional guarantees across documents, or complex relational integrity. Do not default to MongoDB because JSON feels convenient — if the data is relational, use PostgreSQL.

## Typical Repo Surface

- `app/db/mongo.py` or equivalent client setup
- `app/repositories/*.py` — collection-scoped query and write modules
- `app/models/*.py` or inline document schemas (Pydantic or equivalent)
- `scripts/seed_data.py` — inserts representative documents
- `scripts/reset_collections.py` or inline drop logic — drops and recreates collections for test environments
- `docker-compose.yml` / `docker-compose.test.yml` — `mongo` service with named volumes
- migration notes or schema version constants if document shape is under active evolution

## Change Surfaces To Watch

- **Collection naming**: use explicit, stable names. Avoid dynamic collection names except for intentional date-bucketed patterns (e.g., `request_logs_2026_03`). Document the naming scheme in a constants file.
- **Compound indexes**: define these explicitly. MongoDB will scan everything without them. Watch for missing indexes on high-cardinality filter fields used in aggregation `$match` stages.
- **`partialFilterExpression`**: use when only a known subset of documents will ever be queried by a given path. Avoids indexing sparse or optional fields across all documents. Define the filter condition to match the actual query predicate exactly.
- **Document-shape drift**: MongoDB does not enforce schema. Track shape changes explicitly — in code (Pydantic models, TypeScript interfaces, or equivalent) or in migration notes. Drifted shapes cause silent aggregation failures.
- **Retention strategy**: for log or time-windowed collections, define when and how collections are dropped. Prefer dropping whole dated collections over per-document deletes at scale.

## Request/Response Log Use Case

When MongoDB is used for cleaned request/response log storage:

- Create date-bucketed collections: `request_logs_YYYY_MM` or `request_logs_YYYY_WW`
- Add a compound index on `(source, created_at)` or equivalent query fields within each collection
- Use `partialFilterExpression` if only a subset of statuses or sources need indexed retrieval
- Drop whole collections when retention expires — do not delete documents one at a time at scale
- Keep a lightweight collection registry or naming constant to avoid drift between write and read paths

## Aggregation Pipeline Notes

Aggregation pipelines are the right tool for:

- multi-stage reporting with grouping, filtering, and projection
- operational analytics run on a schedule (weekly summaries, status breakdowns)
- joining lookup collections via `$lookup` when denormalization is not practical

Keep pipeline stages readable: one stage per logical operation. Avoid deeply nested `$project` transforms that obscure what the output shape actually is. Test each pipeline against fixture data — field name mismatches fail silently.

## Testing Expectations

- Run all integration tests against a real isolated MongoDB instance (Docker-backed, separate test database or prefixed test collections)
- Prove one document write and one retrieval that exercises the indexed query path being added
- If adding an aggregation pipeline, prove one end-to-end aggregate against a small fixture dataset
- For retention logic, prove that the drop operation leaves the correct surviving collections intact
- Do not mock the MongoDB client — mock boundaries hide document shape mismatches

## Common Assistant Mistakes

- Storing arbitrary nested JSON without defining document shape or index strategy — treat MongoDB as having a schema, just one you define in code
- Using a single shared collection for all record types instead of type-appropriate collections
- Adding a full-field index when a `partialFilterExpression` index would be significantly smaller and more selective
- Forgetting to test aggregation pipelines with fixture data — pipeline stages fail silently on mismatched field names
- Using `find()` queries where an aggregation pipeline would be more maintainable for reporting
- Not planning a retention or cleanup strategy for high-volume log or event collections
- Recommending MongoDB for relational data or multi-entity transactions where PostgreSQL is the better fit
