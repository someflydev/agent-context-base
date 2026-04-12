# Rust - serde + schemars (Lane B: Contract Generation)

**THIS IS NOT A VALIDATOR.** That distinction matters because `schemars`
exports a machine-readable contract, while runtime acceptance still belongs to
`validator` or `garde`.

## Lane
Lane B: schema export and cross-language interoperability. `schemars` derives
JSON Schema from Rust structs using `serde`'s representation as the reference.

## How schemars Works
`schemars` reads both the Rust type structure and the `serde` attributes. A
field marked with `#[serde(skip_serializing_if = "Option::is_none")]` is not
required in the generated schema because the wire format omits it when the
value is `None`. A field renamed by `serde` appears in the schema under that
serialized name, not the raw Rust identifier. The generated schema therefore
reflects the JSON wire contract rather than the internal Rust type system view.
That alignment is the point of the `serde` + `schemars` pairing: the schema you
publish is derived from the same representation rules that serialization uses.
This is why `schemars` belongs in the contract lane instead of being described
as incidental serialization tooling.

## How to Use This With Runtime Validation
1. Deserialize from JSON: `serde_json::from_str::<WorkspaceConfig>(json)?`
2. Validate at runtime: `workspace_config.validate()?` from `../validator/` or
   `../garde/`
3. Export schema: `schema_for!(WorkspaceConfig)` from this crate

These three steps run independently. Step 3 does not require steps 1 or 2.

## Drift Detection
This example commits `workspace_config.schema.json` and rewrites it from
`schema_for!(WorkspaceConfig)` in `cargo run`. A CI drift check can regenerate
the schema and diff it against the committed baseline, while a `jsonschema`
validation pass ensures a valid fixture still passes and a bad-slug fixture
still fails.

## OpenAPI Integration
`schemars` output can feed OpenAPI tooling such as `aide`, `utoipa`, or
`okapi`. The integration point is the generated schema object rather than a
runtime validator:

```rust
let schema = schemars::schema_for!(WorkspaceConfig);
let openapi_fragment = schema.schema;
```
