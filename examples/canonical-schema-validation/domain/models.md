# WorkspaceSyncContext Domain Specification

## Overview

WorkspaceSyncContext models a workspace-scoped synchronization system. A
workspace has configuration and limits, sync jobs run against registered
sources, webhook events report outcomes, and review requests can be opened for
content touched by the sync pipeline. The domain is deliberately compact but
rich enough to surface runtime validation, contract generation, and hybrid
type-driven tradeoffs across all seven target languages.

## Design Goals

- Nested objects through `WorkspaceConfig.settings`
- Enum and tagged variant handling through `SyncRun.status` and
  `WebhookPayload.event_type`
- Clear nullable versus required semantics for timestamp and note fields
- Collection constraints for tags, reviewer emails, content IDs, and headers
- Cross-field validation such as plan limits, timestamp ordering, and
  source-type-specific requirements
- Datetime parsing and coercion sensitivity across library styles
- Boundary validation for counts, lengths, URL formats, and signature format
- Discriminated unions that require dispatch based on a tag field

## Model Definitions

Use the following pseudocode as the canonical language-agnostic contract.
Fields are listed as `field: Type | constraints | notes`.

### SettingsBlock

- `retry_max: integer | 0..10 | inclusive`
- `timeout_seconds: integer | 10..3600 | inclusive`
- `notify_on_failure: boolean | required | no coercion assumptions`
- `webhook_url: string | null | valid URL when present, null otherwise`

### WorkspaceConfig

- `id: UUID | string RFC 4122 | required`
- `name: string | min 3, max 100 chars | required`
- `slug: string | lowercase letters, digits, hyphens only |
  pattern ^[a-z][a-z0-9-]{1,48}[a-z0-9]$`
- `owner_email: string | valid email address | required`
- `plan: enum(free | pro | enterprise) | required | tier selector`
- `max_sync_runs: integer | 1..1000 | constrained by plan`
- `settings: SettingsBlock | nested, required | cannot be null`
- `tags: list[string] | 0..20 items | each item 1..50 chars`
- `created_at: datetime | ISO 8601 string | not null, not future-dated`
- `suspended_until: datetime | null | ISO 8601 string when present`

Cross-field rules:

- if `plan == "free"`, `max_sync_runs` must be `1..10`
- if `plan == "pro"`, `max_sync_runs` must be `1..100`
- if `plan == "enterprise"`, `max_sync_runs` may be `1..1000`

### SyncRun

- `run_id: UUID | required | RFC 4122 string`
- `workspace_id: UUID | required | RFC 4122 string`
- `status: enum(pending | running | succeeded | failed | cancelled) | required`
- `trigger: enum(manual | scheduled | webhook) | required`
- `started_at: datetime | null | null when status == pending`
- `finished_at: datetime | null | null when status == pending or running`
- `duration_ms: integer | null | null when not finished; >= 0 when present`
- `records_ingested: integer | null | null when status != succeeded;
  0..10_000_000 when present`
- `error_code: string | null | present only when status == failed`

Cross-field rules:

- if `finished_at` is present, `started_at` must also be present
- if `finished_at` is present, `finished_at` must be greater than or equal to
  `started_at`
- if `finished_at` is present, `duration_ms` must be present
- if `status == "failed"`, `error_code` must be present
- if `status != "failed"`, `error_code` must be null

### WebhookPayload

- `event_type: enum(sync.completed | sync.failed | workspace.suspended) |
  required | discriminant`
- `payload_version: string | one of "v1", "v2", "v3" | required`
- `timestamp: string | parseable ISO 8601 datetime | multiple common forms accepted`
- `signature: string | lowercase hex, exactly 64 chars |
  HMAC-SHA256 representation`
- `data: discriminated union | structure depends on event_type | required`

When `event_type == "sync.completed"`:

- `SyncCompletedData.run_id: UUID | required`
- `SyncCompletedData.workspace_id: UUID | required`
- `SyncCompletedData.duration_ms: integer | >= 0 | required`
- `SyncCompletedData.records_ingested: integer | 0..10_000_000 | required`

When `event_type == "sync.failed"`:

- `SyncFailedData.run_id: UUID | required`
- `SyncFailedData.workspace_id: UUID | required`
- `SyncFailedData.error_code: string | required | non-empty`
- `SyncFailedData.error_message: string | max 500 chars | required`

When `event_type == "workspace.suspended"`:

- `WorkspaceSuspendedData.workspace_id: UUID | required`
- `WorkspaceSuspendedData.suspended_until: datetime | required`
- `WorkspaceSuspendedData.reason: enum(policy_violation | payment_failure |
  manual) | required`

### IngestionSource

- `source_id: UUID | required | RFC 4122 string`
- `source_type: enum(http_poll | webhook_push | file_watch | database_cdc) |
  required | discriminant`
- `config: discriminated union on source_type | required | see variants below`
- `enabled: boolean | required | no null allowed`
- `poll_interval_seconds: integer | null | source-type-specific`

When `source_type == "http_poll"`:

- `HttpPollConfig.url: string | valid URL | required`
- `HttpPollConfig.method: enum(GET | POST) | required`
- `HttpPollConfig.headers: map[string, string] | 0..20 entries | required`

When `source_type == "webhook_push"`:

- `WebhookPushConfig.path: string | starts with "/" | required`
- `WebhookPushConfig.secret: string | required | non-empty`

When `source_type == "file_watch"`:

- `FileWatchConfig.path: string | required | file-system path`
- `FileWatchConfig.pattern: string | required | glob expression`

When `source_type == "database_cdc"`:

- `DatabaseCdcConfig.dsn: string | required | connection string`
- `DatabaseCdcConfig.table: string | required | table or relation name`
- `DatabaseCdcConfig.cursor_field: string | required | change cursor column`

Cross-field rules:

- if `source_type == "http_poll"`, `poll_interval_seconds` must be present and
  greater than or equal to `60`
- if `source_type != "http_poll"`, `poll_interval_seconds` must be null

### ReviewRequest

- `request_id: UUID | required | RFC 4122 string`
- `workspace_id: UUID | required | RFC 4122 string`
- `reviewer_emails: list[string] | 1..5 items | each must be a valid email and
  the list must have no duplicates`
- `content_ids: list[UUID] | 1..50 items | no duplicates`
- `priority: enum(low | normal | high | critical) | required`
- `due_at: datetime | null | required when priority == critical`
- `notes: string | null | max 2000 chars when present`

Cross-field rules:

- if `priority == "critical"`, `due_at` must be present

## Library-Specific Considerations

- Coercion: Some libraries parse `"2024-01-15T12:00:00Z"` into a datetime
  automatically, including Pydantic and `Ecto.Changeset`. Others require a
  separate decode or parse step before validation, especially Go and Rust
  runtime-validator flows. Document that choice per example and do not treat it
  as a parity failure by itself.
- Nullable versus optional: Some ecosystems collapse null and absent handling
  more readily, especially Ruby and Elixir. Others distinguish them explicitly,
  such as TypeScript and Rust with `Option<T>`-style modeling. Examples must
  call this out when the fixture corpus depends on explicit nulls.
- Error accumulation: Pydantic, Zod, Konform, and dry-validation commonly
  accumulate multiple errors. Go validator and Rust validator may report one or
  many depending on the setup. Parity requires rejection, not an exact error
  count.
- Discriminated unions: Rust enums, TypeScript discriminated unions, and Kotlin
  sealed hierarchies map naturally to `WebhookPayload.data`. Go and Ruby
  usually need manual dispatch. Each example should show the idiomatic approach
  for its language rather than force a uniform implementation style.
