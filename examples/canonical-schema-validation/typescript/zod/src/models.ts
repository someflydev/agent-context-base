import { z } from "zod";

const slugRegex = /^[a-z][a-z0-9-]{1,48}[a-z0-9]$/;
const hex64Regex = /^[a-f0-9]{64}$/;

/**
 * Lane C demonstration: the same Zod schema provides runtime validation,
 * TypeScript inference via z.infer<>, and JSON Schema export later.
 */
export const SettingsBlockSchema = z.object({
  retry_max: z.number().int().min(0).max(10),
  timeout_seconds: z.number().int().min(10).max(3600),
  notify_on_failure: z.boolean(),
  webhook_url: z.string().url().nullable(),
});

/**
 * Lane C WorkspaceConfig schema with superRefine for cross-field plan limits.
 */
export const WorkspaceConfigSchema = z
  .object({
    id: z.string().uuid(),
    name: z.string().min(3).max(100),
    slug: z.string().regex(slugRegex),
    owner_email: z.string().email(),
    plan: z.enum(["free", "pro", "enterprise"]),
    max_sync_runs: z.number().int().min(1).max(1000),
    settings: SettingsBlockSchema,
    tags: z.array(z.string().min(1).max(50)).max(20),
    created_at: z.string().datetime(),
    suspended_until: z.string().datetime().nullable(),
  })
  .superRefine((value, ctx) => {
    if (value.plan === "free" && value.max_sync_runs > 10) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "free plan supports at most 10 sync runs", path: ["max_sync_runs"] });
    }
    if (value.plan === "pro" && value.max_sync_runs > 100) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "pro plan supports at most 100 sync runs", path: ["max_sync_runs"] });
    }
  });

/**
 * Lane C SyncRun schema with superRefine for timeline and failed-run rules.
 */
export const SyncRunSchema = z
  .object({
    run_id: z.string().uuid(),
    workspace_id: z.string().uuid(),
    status: z.enum(["pending", "running", "succeeded", "failed", "cancelled"]),
    trigger: z.enum(["manual", "scheduled", "webhook"]),
    started_at: z.string().datetime().nullable(),
    finished_at: z.string().datetime().nullable(),
    duration_ms: z.number().int().min(0).nullable(),
    records_ingested: z.number().int().min(0).max(10_000_000).nullable(),
    error_code: z.string().nullable(),
  })
  .superRefine((value, ctx) => {
    if (value.finished_at && !value.started_at) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "finished_at requires started_at", path: ["finished_at"] });
    }
    if (value.started_at && value.finished_at && value.finished_at < value.started_at) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "finished_at must be >= started_at", path: ["finished_at"] });
    }
    if (value.finished_at && value.duration_ms === null) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "duration_ms required when finished", path: ["duration_ms"] });
    }
    if (value.status === "failed" && !value.error_code) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "failed sync runs require error_code", path: ["error_code"] });
    }
    if (value.status !== "failed" && value.error_code !== null) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "error_code must be null unless failed", path: ["error_code"] });
    }
  });

const SyncCompletedDataSchema = z.object({
  event_type: z.literal("sync.completed"),
  run_id: z.string().uuid(),
  workspace_id: z.string().uuid(),
  duration_ms: z.number().int().min(0),
  records_ingested: z.number().int().min(0).max(10_000_000),
});

const SyncFailedDataSchema = z.object({
  event_type: z.literal("sync.failed"),
  run_id: z.string().uuid(),
  workspace_id: z.string().uuid(),
  error_code: z.string().min(1),
  error_message: z.string().min(1).max(500),
});

const WorkspaceSuspendedDataSchema = z.object({
  event_type: z.literal("workspace.suspended"),
  workspace_id: z.string().uuid(),
  suspended_until: z.string().datetime(),
  reason: z.enum(["policy_violation", "payment_failure", "manual"]),
});

const WebhookDataSchema = z.discriminatedUnion("event_type", [
  SyncCompletedDataSchema,
  SyncFailedDataSchema,
  WorkspaceSuspendedDataSchema,
]);

/**
 * Lane C WebhookPayload schema using a discriminated union for the tagged data variants.
 */
export const WebhookPayloadSchema = z
  .object({
    event_type: z.enum(["sync.completed", "sync.failed", "workspace.suspended"]),
    payload_version: z.enum(["v1", "v2", "v3"]),
    timestamp: z.string().datetime(),
    signature: z.string().regex(hex64Regex),
    data: z.record(z.unknown()),
  })
  .superRefine((value, ctx) => {
    const parsed = WebhookDataSchema.safeParse({ event_type: value.event_type, ...value.data });
    if (!parsed.success) {
      for (const issue of parsed.error.issues) {
        ctx.addIssue({ ...issue, path: ["data", ...issue.path.filter((part) => part !== "event_type")] });
      }
    }
  });

const HttpPollConfigSchema = z.object({
  source_type: z.literal("http_poll"),
  url: z.string().url(),
  method: z.enum(["GET", "POST"]),
  headers: z.record(z.string()).refine((value) => Object.keys(value).length <= 20, "at most 20 headers"),
});

const WebhookPushConfigSchema = z.object({
  source_type: z.literal("webhook_push"),
  path: z.string().regex(/^\//),
  secret: z.string().min(1),
});

const FileWatchConfigSchema = z.object({
  source_type: z.literal("file_watch"),
  path: z.string().min(1),
  pattern: z.string().min(1),
});

const DatabaseCdcConfigSchema = z.object({
  source_type: z.literal("database_cdc"),
  dsn: z.string().min(1),
  table: z.string().min(1),
  cursor_field: z.string().min(1),
});

const IngestionConfigSchema = z.discriminatedUnion("source_type", [
  HttpPollConfigSchema,
  WebhookPushConfigSchema,
  FileWatchConfigSchema,
  DatabaseCdcConfigSchema,
]);

/**
 * Lane C IngestionSource schema with a discriminated union plus cross-field checks.
 */
export const IngestionSourceSchema = z
  .object({
    source_id: z.string().uuid(),
    source_type: z.enum(["http_poll", "webhook_push", "file_watch", "database_cdc"]),
    config: z.record(z.unknown()),
    enabled: z.boolean(),
    poll_interval_seconds: z.number().int().min(60).nullable(),
  })
  .superRefine((value, ctx) => {
    const parsed = IngestionConfigSchema.safeParse({ source_type: value.source_type, ...value.config });
    if (!parsed.success) {
      for (const issue of parsed.error.issues) {
        ctx.addIssue({ ...issue, path: ["config", ...issue.path.filter((part) => part !== "source_type")] });
      }
    }
    if (value.source_type === "http_poll" && value.poll_interval_seconds === null) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "http_poll sources require poll_interval_seconds", path: ["poll_interval_seconds"] });
    }
    if (value.source_type !== "http_poll" && value.poll_interval_seconds !== null) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "poll_interval_seconds must be null for non-http_poll sources", path: ["poll_interval_seconds"] });
    }
  });

/**
 * Lane C ReviewRequest schema with duplicate checks and critical due-date rules.
 */
export const ReviewRequestSchema = z
  .object({
    request_id: z.string().uuid(),
    workspace_id: z.string().uuid(),
    reviewer_emails: z.array(z.string().email()).min(1).max(5),
    content_ids: z.array(z.string().uuid()).min(1).max(50),
    priority: z.enum(["low", "normal", "high", "critical"]),
    due_at: z.string().datetime().nullable(),
    notes: z.string().max(2000).nullable(),
  })
  .superRefine((value, ctx) => {
    if (new Set(value.reviewer_emails).size !== value.reviewer_emails.length) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "reviewer_emails must be unique", path: ["reviewer_emails"] });
    }
    if (new Set(value.content_ids).size !== value.content_ids.length) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "content_ids must be unique", path: ["content_ids"] });
    }
    if (value.priority === "critical" && value.due_at === null) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: "critical review requests require due_at", path: ["due_at"] });
    }
  });

export type SettingsBlock = z.infer<typeof SettingsBlockSchema>;
export type WorkspaceConfig = z.infer<typeof WorkspaceConfigSchema>;
export type SyncRun = z.infer<typeof SyncRunSchema>;
export type WebhookPayload = z.infer<typeof WebhookPayloadSchema>;
export type IngestionSource = z.infer<typeof IngestionSourceSchema>;
export type ReviewRequest = z.infer<typeof ReviewRequestSchema>;
