# Python - Pydantic (Lane C: Hybrid Type-Driven)

## Lane
Lane C means the `BaseModel` definition is the type, the runtime validator,
and the JSON Schema source at the same time. One definition drives all three
surfaces, which is why Pydantic is the clearest Python hybrid example.

## Models
- `SettingsBlock` validates URL shape when `webhook_url` is present.
- `WorkspaceConfig` enforces slug, email, tag, and plan-limit rules.
- `SyncRun` enforces timestamp ordering, duration requirements, and error-code rules.
- `WebhookPayload` manually dispatches tagged payload variants from the outer discriminator.
- `IngestionSource` dispatches source-specific config models and enforces poll rules.
- `ReviewRequest` validates reviewer emails, duplicate detection, and critical due dates.

## Key Pydantic v2 Patterns Used
- `model_validator(mode="after")` for plan limits, timeline checks, and uniqueness rules.
- `field_validator` for slug, email, URL, signature, and collection item checks.
- Manual tagged-union dispatch where the shared fixture corpus keeps the discriminator outside the nested object.
- `Field()` constraints for lengths, numeric bounds, and nullable defaults.
- `Enum` types for plan, status, trigger, source, and priority fields.

## Comparison with marshmallow
Pydantic starts from type annotations and turns them directly into runtime
validation and JSON Schema export. That makes it strong for model-driven
workflows where static and runtime behavior need to stay aligned. marshmallow
uses explicit `Schema` classes instead, which gives more control over load and
dump behavior but separates the data model from the validation object.

## Running
```bash
python3 schema_export.py
python3 -m unittest verification/schema-validation/python/test_pydantic.py
```

## Smoke Tests
The Python smoke coverage lives in
`verification/schema-validation/python/test_pydantic.py`.
