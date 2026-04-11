# Schema Validation Canonical Examples — Catalog

## Status Legend

- `[ ]` planned — not yet implemented
- `[~]` stub — directory exists, no working code yet
- `[x]` implemented — working code with passing smoke tests
- `[!]` gap — expected but blocked; reason documented

## Python

| Status | Library | Lane | Path | Notes |
| --- | --- | --- | --- | --- |
| [ ] | Pydantic | C | python/pydantic/ | Hybrid: type=validator=schema |
| [ ] | marshmallow | A | python/marshmallow/ | Explicit schema, serialization |

## TypeScript

| Status | Library | Lane | Path | Notes |
| --- | --- | --- | --- | --- |
| [ ] | Zod | C | typescript/zod/ | Mainstream hybrid |
| [ ] | Valibot | A | typescript/valibot/ | Modular, lightweight |
| [ ] | io-ts | A | typescript/io-ts/ | Codec/FP approach |
| [ ] | TypeBox + Ajv | B | typescript/typebox-ajv/ | Contract-first, JSON Schema |

## Go

| Status | Library | Lane | Path | Notes |
| --- | --- | --- | --- | --- |
| [ ] | go-playground/validator | A | go/go-playground-validator/ | Tag-based struct validation |
| [ ] | ozzo-validation | A | go/ozzo-validation/ | Code-driven explicit rules |
| [ ] | OpenAPI generation | B | go/openapi-generation/ | External contract lane; swaggo |

## Rust

| Status | Library | Lane | Path | Notes |
| --- | --- | --- | --- | --- |
| [ ] | validator | A | rust/validator/ | Derive-based struct validation |
| [ ] | garde | A | rust/garde/ | Richer rule DSL |
| [ ] | serde + schemars | B | rust/serde-schemars/ | CONTRACT lane: JSON Schema from serde |

## Kotlin

| Status | Library | Lane | Path | Notes |
| --- | --- | --- | --- | --- |
| [ ] | Konform | A | kotlin/konform/ | Kotlin-first DSL |
| [ ] | Hibernate Validator | A | kotlin/hibernate-validator/ | JVM annotation standard |

## Ruby

| Status | Library | Lane | Path | Notes |
| --- | --- | --- | --- | --- |
| [ ] | dry-validation | A | ruby/dry-validation/ | Rich rule contracts |
| [ ] | dry-schema | A/B | ruby/dry-schema/ | Schema layer; JSON Schema output |

## Elixir

| Status | Library | Lane | Path | Notes |
| --- | --- | --- | --- | --- |
| [ ] | Ecto.Changeset | A | elixir/ecto-changeset/ | Dominant boundary validator |
| [ ] | Norm | A | elixir/norm/ | Declarative spec alternative |
| [ ] | ex_json_schema | B | elixir/ex-json-schema/ | JSON Schema contract lane |

## Cross-Language Summary

| Language | Native Hybrid Lane |
| --- | --- |
| Python | ✓ Pydantic |
| TypeScript | ✓ Zod, io-ts |
| Go | ✗ explicit runtime and contract tooling stay separate |
| Rust | ✗ serde/schemars and runtime validators are intentionally split |
| Kotlin | ✗ framework contracts and runtime validation are separate concerns |
| Ruby | ✗ runtime schemas and contract export are separate library surfaces |
| Elixir | ✗ boundary validation and JSON Schema tooling remain distinct |
