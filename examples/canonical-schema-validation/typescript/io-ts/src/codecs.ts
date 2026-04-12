/*
io-ts codecs are runtime values, not passive type declarations.
Each codec carries both a static TypeScript view and decode/encode behavior.
Calling decode() does not throw a ValidationError.
Instead, io-ts returns Either<Errors, T>, which forces the caller to decide
how to handle invalid input at the boundary.
That explicit functional style is different from Zod's parse()/safeParse()
ergonomics and different from Pydantic's exception-driven model creation.
Cross-field validation also looks different: you build a refined codec value
on top of a structural codec instead of attaching a method to a schema object.
Use io-ts when you want codec algebra and explicit error typing.
Do not use it expecting a simpler Zod.
*/

import * as E from "fp-ts/lib/Either.js";
import * as t from "io-ts";

const slugRegex = /^[a-z][a-z0-9-]{1,48}[a-z0-9]$/;

const NullableString = t.union([t.string, t.null]);
const NullableNumber = t.union([t.number, t.null]);

export const SettingsBlockCodec = t.type({
  retry_max: t.number,
  timeout_seconds: t.number,
  notify_on_failure: t.boolean,
  webhook_url: NullableString,
});

const WorkspaceConfigShape = t.type({
  id: t.string,
  name: t.string,
  slug: t.string,
  owner_email: t.string,
  plan: t.keyof({ free: null, pro: null, enterprise: null }),
  max_sync_runs: t.number,
  settings: SettingsBlockCodec,
  tags: t.array(t.string),
  created_at: t.string,
  suspended_until: NullableString,
});

export const WorkspaceConfigCodec = new t.Type<t.TypeOf<typeof WorkspaceConfigShape>, t.OutputOf<typeof WorkspaceConfigShape>, unknown>(
  "WorkspaceConfigCodec",
  WorkspaceConfigShape.is,
  (input, context) =>
    E.chain((value: t.TypeOf<typeof WorkspaceConfigShape>) => {
      if (!slugRegex.test(value.slug)) {
        return t.failure(input, context, "slug must match the canonical pattern");
      }
      if (value.plan === "free" && value.max_sync_runs > 10) {
        return t.failure(input, context, "free plan supports at most 10 sync runs");
      }
      if (value.plan === "pro" && value.max_sync_runs > 100) {
        return t.failure(input, context, "pro plan supports at most 100 sync runs");
      }
      return t.success(value);
    })(WorkspaceConfigShape.validate(input, context)),
  WorkspaceConfigShape.encode,
);

const SyncRunShape = t.type({
  run_id: t.string,
  workspace_id: t.string,
  status: t.keyof({ pending: null, running: null, succeeded: null, failed: null, cancelled: null }),
  trigger: t.keyof({ manual: null, scheduled: null, webhook: null }),
  started_at: NullableString,
  finished_at: NullableString,
  duration_ms: NullableNumber,
  records_ingested: NullableNumber,
  error_code: NullableString,
});

export const SyncRunCodec = new t.Type<t.TypeOf<typeof SyncRunShape>, t.OutputOf<typeof SyncRunShape>, unknown>(
  "SyncRunCodec",
  SyncRunShape.is,
  (input, context) =>
    E.chain((value: t.TypeOf<typeof SyncRunShape>) => {
      if (value.finished_at && !value.started_at) {
        return t.failure(input, context, "finished_at requires started_at");
      }
      if (value.started_at && value.finished_at && value.finished_at < value.started_at) {
        return t.failure(input, context, "finished_at must be >= started_at");
      }
      if (value.finished_at && value.duration_ms === null) {
        return t.failure(input, context, "duration_ms is required when finished_at is present");
      }
      if (value.status === "failed" && !value.error_code) {
        return t.failure(input, context, "failed sync runs require error_code");
      }
      if (value.status !== "failed" && value.error_code !== null) {
        return t.failure(input, context, "error_code must be null unless status is failed");
      }
      return t.success(value);
    })(SyncRunShape.validate(input, context)),
  SyncRunShape.encode,
);

// In io-ts, decoding returns Either<Errors, T>; callers pattern-match on Left/Right.
export const decodeSyncRun = (rawData: unknown) => SyncRunCodec.decode(rawData);

export type SettingsBlock = t.TypeOf<typeof SettingsBlockCodec>;
export type WorkspaceConfig = t.TypeOf<typeof WorkspaceConfigCodec>;
export type SyncRun = t.TypeOf<typeof SyncRunCodec>;
