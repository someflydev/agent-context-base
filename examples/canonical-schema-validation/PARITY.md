# Cross-Language Parity Rules

## Purpose

Parity in this arc means every language implements the same WorkspaceSyncContext
domain, uses the same fixtures, and demonstrates comparable acceptance and
rejection behavior. It does not require identical error text, identical API
shapes, or identical implementation style.

## Universally Required Behavior

1. All fixtures in `domain/fixtures/valid/` must be accepted without errors.
2. All fixtures in `domain/fixtures/invalid/` must be rejected with at least
   one validation error. Error message format is implementation-defined.
3. Error accumulation may return the first error or many errors. Smoke tests
   must assert at least one error, not a specific error count.
4. `WorkspaceConfig.plan` cross-field limits for `max_sync_runs` must be
   enforced. `invalid/workspace_config_plan_too_many_runs.json` must be
   rejected by all Lane A implementations.
5. `SyncRun.finished_at >= started_at` must be enforced.
   `invalid/sync_run_timestamps_inverted.json` must be rejected.
6. `ReviewRequest.due_at` is required when `priority == critical`.
   `invalid/review_request_critical_no_due_date.json` must be rejected.
7. `IngestionSource.poll_interval_seconds` is required for `http_poll`.
   `invalid/ingestion_source_poll_interval_missing.json` must be rejected.

## Lane B Required Behavior

1. The exported JSON Schema must be valid JSON and must parse without error.
2. The exported schema must include all five models or at minimum the primary
   model `WorkspaceConfig`, with field names matching `domain/models.md`.
3. The exported schema must reject
   `invalid/workspace_config_bad_slug.json` in a round-trip drift check.
4. The exported schema must accept `valid/workspace_config_full.json`.

## Documented Divergences

| Fixture | Behavior | Languages where X happens | Languages where Y happens | Why |
| --- | --- | --- | --- | --- |
| `edge/webhook_payload_unknown_event_type.json` | Accept vs reject | Some libraries accept unknown enum values during looser decode flows | Others strict-reject immediately | Enum strictness varies |
| `edge/review_request_duplicate_content_ids.json` | Accept vs reject | Languages without explicit dedup validation may accept | Those with explicit uniqueness rules reject | Duplicate detection requires an explicit rule |
| Datetime coercion | Auto-parse vs error | Pydantic, Ecto auto-parse ISO 8601 strings | Go validator, Rust validator require pre-parsed values or extra decode steps | Library philosophy |
| Null vs absent fields | Treated same vs different | Ruby, Elixir often treat null and absent similarly | TypeScript and Rust distinguish optionality from nullability | Type system |

## Smoke Test Assertions That Are Explicitly OUT OF SCOPE for Parity

- Specific error message text
- Error field names
- Stack trace format
- Performance characteristics
- Serialization format of error objects
