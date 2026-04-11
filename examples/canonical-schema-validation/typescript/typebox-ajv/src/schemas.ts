import { Static, Type } from "@sinclair/typebox";

export const SettingsBlockSchema = Type.Object({
  retry_max: Type.Integer({ minimum: 0, maximum: 10 }),
  timeout_seconds: Type.Integer({ minimum: 10, maximum: 3600 }),
  notify_on_failure: Type.Boolean(),
  webhook_url: Type.Union([Type.String({ format: "uri" }), Type.Null()]),
});

// TypeBox schemas ARE JSON Schema objects natively.
export const WorkspaceConfigSchema = Type.Intersect([
  Type.Object({
    id: Type.String({ format: "uuid" }),
    name: Type.String({ minLength: 3, maxLength: 100 }),
    slug: Type.String({ pattern: "^[a-z][a-z0-9-]{1,48}[a-z0-9]$" }),
    owner_email: Type.String({ format: "email" }),
    plan: Type.Union([Type.Literal("free"), Type.Literal("pro"), Type.Literal("enterprise")]),
    max_sync_runs: Type.Integer({ minimum: 1, maximum: 1000 }),
    settings: SettingsBlockSchema,
    tags: Type.Array(Type.String({ minLength: 1, maxLength: 50 }), { maxItems: 20 }),
    created_at: Type.String({ format: "date-time" }),
    suspended_until: Type.Union([Type.String({ format: "date-time" }), Type.Null()]),
  }),
  Type.Union([
    Type.Object({
      plan: Type.Literal("free"),
      max_sync_runs: Type.Integer({ minimum: 1, maximum: 10 }),
    }),
    Type.Object({
      plan: Type.Literal("pro"),
      max_sync_runs: Type.Integer({ minimum: 1, maximum: 100 }),
    }),
    Type.Object({
      plan: Type.Literal("enterprise"),
      max_sync_runs: Type.Integer({ minimum: 1, maximum: 1000 }),
    }),
  ]),
]);

// Cross-field rules beyond this pattern still require application-level logic or
// more advanced JSON Schema if/then/else composition.
export const SyncRunSchema = Type.Object({
  run_id: Type.String({ format: "uuid" }),
  workspace_id: Type.String({ format: "uuid" }),
  status: Type.Union([
    Type.Literal("pending"),
    Type.Literal("running"),
    Type.Literal("succeeded"),
    Type.Literal("failed"),
    Type.Literal("cancelled"),
  ]),
  trigger: Type.Union([Type.Literal("manual"), Type.Literal("scheduled"), Type.Literal("webhook")]),
  started_at: Type.Union([Type.String({ format: "date-time" }), Type.Null()]),
  finished_at: Type.Union([Type.String({ format: "date-time" }), Type.Null()]),
  duration_ms: Type.Union([Type.Integer({ minimum: 0 }), Type.Null()]),
  records_ingested: Type.Union([Type.Integer({ minimum: 0, maximum: 10000000 }), Type.Null()]),
  error_code: Type.Union([Type.String(), Type.Null()]),
});

export type SettingsBlock = Static<typeof SettingsBlockSchema>;
export type WorkspaceConfig = Static<typeof WorkspaceConfigSchema>;
export type SyncRun = Static<typeof SyncRunSchema>;
