# Contract Generation Path Selection

Use this skill to choose the correct schema-export and drift-detection path for
the target language.

## Procedure

1. Identify the output artifact type.
   - JSON Schema document
   - OpenAPI fragment or full spec
   - custom schema export
   For this arc, JSON Schema and OpenAPI are the primary targets.

2. Route by language to the correct generation path.
   - Python: Pydantic `model_json_schema()` or equivalent model schema export;
     `marshmallow-jsonschema` for marshmallow schemas
   - TypeScript: TypeBox schemas are JSON Schema natively; use
     `zod-to-json-schema` for Zod and `ts-json-schema-generator` only when the
     task is raw-type driven
   - Go: external tooling such as `swaggo`, `kin-openapi`, or manual schema
     composition; state explicitly that Go lacks one dominant unified path
   - Rust: `schemars::schema_for!()` aligned with `serde`; pair with `okapi` or
     `aide` when the task is OpenAPI
   - Kotlin: `springdoc-openapi` for Spring surfaces; `kotlinx.serialization`
     plus schema tooling for non-Spring contexts
   - Ruby: `json_schemer`, dry-schema JSON Schema output, or manual composition
   - Elixir: `ex_json_schema` for JSON Schema validation and export workflows

3. Confirm whether drift detection is in scope.
   Drift detection matters when a downstream consumer relies on the exported
   schema, when runtime validation and schema export are maintained separately,
   or when serialization shape can move independently from validation rules.

4. If drift detection is in scope, load
   `examples/canonical-schema-validation/PARITY.md` when it exists.
   During PROMPT_113 foundation work, note that the parity rules are scheduled
   for PROMPT_114 and later and should be loaded once present.

5. Recommend a round-trip drift check.
   - serialize a known-valid object
   - validate the serialized form against the exported schema
   - assert that the runtime validator accepts the same object
   - repeat with a known-invalid object and assert both paths reject it

6. For Rust, emphasize the `serde` representation explicitly.
   If `serde` rename or serialization attributes change, `schemars` output can
   move even when runtime rule code in `validator` or `garde` stays the same.

7. For Go, acknowledge the ergonomic gap directly.
   Do not describe external OpenAPI tooling as if it were equivalent to
   Pydantic or Zod's inline model-driven export path.

8. For TypeScript, choose between hybrid and contract-native paths honestly.
   Use TypeBox + Ajv when JSON Schema is the first-class artifact. Use Zod when
   runtime ergonomics drive the decision and schema export is secondary.

9. Do not call a schema export drift-free unless the round-trip check actually
   ran. Generation alone proves that a file exists, not that the contract still
   matches runtime behavior.

## Good Triggers

- "export JSON Schema from my model"
- "generate OpenAPI from my types"
- "does my schema match my runtime validation"
- "drift between schema and validator"
- "contract-first workflow in Go"
- "schemars for OpenAPI in Rust"

## Avoid

- treating schema export as complete without a drift check when downstream consumers are mentioned
- recommending manual JSON Schema composition when a derive macro or helper already exists
- presenting Go's contract path as equivalent to Pydantic's inline derivation
- implying that runtime validation and exported contracts stay aligned automatically

## Reference Files

- `context/doctrine/schema-validation-contracts.md`
- `context/stacks/schema-validation-{language}.yaml`
- `examples/canonical-schema-validation/PARITY.md`
- `examples/canonical-schema-validation/CATALOG.md`
