import * as v from "valibot";

const slugRegex = /^[a-z][a-z0-9-]{1,48}[a-z0-9]$/;

// Valibot uses pipe() instead of method chaining. Validators are tree-shakeable,
// so only the imported pipes participate in the final bundle.
export const SettingsBlockSchema = v.object({
  retry_max: v.pipe(v.number(), v.integer(), v.minValue(0), v.maxValue(10)),
  timeout_seconds: v.pipe(v.number(), v.integer(), v.minValue(10), v.maxValue(3600)),
  notify_on_failure: v.boolean(),
  webhook_url: v.nullable(v.pipe(v.string(), v.url())),
});

export const WorkspaceConfigSchema = v.pipe(
  v.object({
    id: v.pipe(v.string(), v.uuid()),
    name: v.pipe(v.string(), v.minLength(3), v.maxLength(100)),
    slug: v.pipe(v.string(), v.regex(slugRegex)),
    owner_email: v.pipe(v.string(), v.email()),
    plan: v.picklist(["free", "pro", "enterprise"]),
    max_sync_runs: v.pipe(v.number(), v.integer(), v.minValue(1), v.maxValue(1000)),
    settings: SettingsBlockSchema,
    tags: v.pipe(v.array(v.pipe(v.string(), v.minLength(1), v.maxLength(50))), v.maxLength(20)),
    created_at: v.pipe(v.string(), v.isoDateTime()),
    suspended_until: v.nullable(v.pipe(v.string(), v.isoDateTime())),
  }),
  v.check((input) => !(input.plan === "free" && input.max_sync_runs > 10), "free plan supports at most 10 sync runs"),
  v.check((input) => !(input.plan === "pro" && input.max_sync_runs > 100), "pro plan supports at most 100 sync runs"),
);

// Valibot composes checks as separate steps rather than adding methods to the schema object.
export const SyncRunSchema = v.pipe(
  v.object({
    run_id: v.pipe(v.string(), v.uuid()),
    workspace_id: v.pipe(v.string(), v.uuid()),
    status: v.picklist(["pending", "running", "succeeded", "failed", "cancelled"]),
    trigger: v.picklist(["manual", "scheduled", "webhook"]),
    started_at: v.nullable(v.pipe(v.string(), v.isoDateTime())),
    finished_at: v.nullable(v.pipe(v.string(), v.isoDateTime())),
    duration_ms: v.nullable(v.pipe(v.number(), v.integer(), v.minValue(0))),
    records_ingested: v.nullable(v.pipe(v.number(), v.integer(), v.minValue(0), v.maxValue(10_000_000))),
    error_code: v.nullable(v.string()),
  }),
  v.check((input) => !(input.finished_at && !input.started_at), "finished_at requires started_at"),
  v.check(
    (input) => !(input.started_at && input.finished_at && input.finished_at < input.started_at),
    "finished_at must be >= started_at",
  ),
  v.check((input) => !(input.finished_at && input.duration_ms === null), "duration_ms required when finished"),
  v.check((input) => !(input.status === "failed" && !input.error_code), "failed sync runs require error_code"),
  v.check((input) => !(input.status !== "failed" && input.error_code !== null), "error_code must be null unless failed"),
);

// Partial stubs for the remaining domain models. This prompt requires the two
// most complex models for Valibot; these names mark the remaining extension points.
export const WebhookPayloadSchema = v.object({
  event_type: v.picklist(["sync.completed", "sync.failed", "workspace.suspended"]),
});

export const IngestionSourceSchema = v.object({
  source_type: v.picklist(["http_poll", "webhook_push", "file_watch", "database_cdc"]),
});

export const ReviewRequestSchema = v.object({
  priority: v.picklist(["low", "normal", "high", "critical"]),
});

export type SettingsBlock = v.InferOutput<typeof SettingsBlockSchema>;
export type WorkspaceConfig = v.InferOutput<typeof WorkspaceConfigSchema>;
export type SyncRun = v.InferOutput<typeof SyncRunSchema>;
