# Elixir - ex_json_schema (Lane B: JSON Schema Contract Workflows)

## Lane
Lane B: validate data against a JSON Schema document. Contract-first.

## What ex_json_schema Does
`ex_json_schema` validates an Elixir map against a JSON Schema document and
returns either `:ok` or `{:error, errors}`. In this lane, the contract is the
source of truth rather than the Elixir module definitions. That makes it a
good fit when the schema is shared across languages or published externally.

## Use Cases
- Validating webhook payloads against a published JSON Schema
- Contract-first API design where the schema is published before implementation
- Drift detection between runtime payloads and a committed schema artifact
- Cross-language compatibility with the same JSON Schema in Python, Rust, and TypeScript

## Comparison with Ecto.Changeset
`ex_json_schema` validates against a schema document. `Ecto.Changeset`
validates against Elixir-side field definitions and pipeline functions. Most
Phoenix apps should reach for `Ecto.Changeset` first; use `ex_json_schema`
when schema-first interoperability is the actual requirement.
