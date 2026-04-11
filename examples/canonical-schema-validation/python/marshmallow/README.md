# Python - marshmallow (Lane A: Explicit Schema Objects)

## Lane
Lane A means the `Schema` class is separate from the data shape. Unlike
Pydantic, marshmallow does not treat type annotations as the source of truth;
you define schema objects explicitly and apply them to raw dicts or data class
instances.

## Key Patterns Used
- `validates_schema` for plan limits, timestamp ordering, and due-date rules.
- `Nested` for `SettingsBlock`.
- Manual dispatch for discriminated unions because marshmallow has no native tagged-union field.
- Plain dict output after validation instead of a generated model class.

## Comparison with Pydantic
marshmallow gives you an explicit schema surface and strong control over load
and dump behavior, which is useful when serialization steps matter as much as
validation. Pydantic is tighter when you want one model definition to drive
types, validation, and schema export together. marshmallow is not worse; it is
just more explicit about the schema object being separate from the data object.

## Running
```bash
python3 -c "from schemas import WorkspaceConfigSchema; print(WorkspaceConfigSchema().fields.keys())"
```

## Smoke Tests
The Python smoke coverage lives in
`verification/schema-validation/python/test_marshmallow.py`.
