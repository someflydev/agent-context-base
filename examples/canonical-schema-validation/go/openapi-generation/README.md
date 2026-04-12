# Go - OpenAPI/JSON Schema Generation (Lane B: Externalized Contract)

## Lane
Lane B: contract generation. Go does not have a single library that derives
JSON Schema from struct definitions the way Pydantic or `schemars` do.

## The Go Contract Generation Gap
Unlike Python with `model_json_schema()` or Rust with `schema_for!()`, Go does
not have one dominant path that unifies model definition and contract export.
`swaggo` extracts OpenAPI metadata from doc comments, which means the contract
surface is partly expressed in comments rather than checked types. Libraries
such as `invopop/jsonschema` and `kin-openapi` exist, but they still require
extra reflection or explicit schema construction choices. That fragmented
tooling is a real ergonomic gap compared with Pydantic or `schemars`, and this
example makes that gap visible instead of pretending it does not exist.

## What This Example Shows
The example includes swaggo-style comments on `models.WorkspaceConfig`, a
hand-authored JSON Schema artifact, and a drift check that validates one valid
fixture and one invalid fixture against the committed schema file.

## Implication for Interoperability
If a Go team needs a machine-readable contract from its structs, it should plan
for explicit integration work. Keep the schema generation path visible in CI
and add drift checks so serde-like representation changes do not silently leave
the contract behind.
