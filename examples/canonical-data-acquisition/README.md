# Canonical Data Acquisition

This directory is the shared entry point for data acquisition guidance.

## Capability Gap

`PROMPT_30` gave the repo strong doctrine and workflow coverage for acquisition-heavy systems. The remaining gap was that the example layer still looked Python-first, which blurred the boundary between cross-language rules and stack-specific implementations.

This directory now separates those concerns:

- doctrine and workflows hold the invariant layer
- this index and support matrix route assistants toward the right stack-specific surface
- stack-specific canonical acquisition examples must be real code with honest verification, not pseudocode

## Invariant Layer

Start here when the stack is undecided or when the user explicitly wants language-agnostic guidance:

- `context/doctrine/data-acquisition-invariants.md`
- `context/doctrine/data-acquisition-philosophy.md`
- `context/workflows/add-api-ingestion-source.md`
- `context/workflows/add-scraping-source.md`
- `context/workflows/add-raw-download-archive.md`
- `context/workflows/add-parser-normalizer.md`
- `context/workflows/add-classification-step.md`
- `context/workflows/add-recurring-sync.md`
- `context/workflows/add-event-driven-sync.md`

Shared files in this directory apply to every stack in this capability area:

- `examples/canonical-data-acquisition/README.md`
- `examples/canonical-data-acquisition/language-support-matrix.yaml`

## Language Matrix

The old Python snippets are not the only canonical surface anymore. At the moment, this capability area has a shared invariant layer and a shared routing layer, but no stack-specific acquisition implementation files have landed yet.

When a stack-specific acquisition example does not exist yet, assistants should say that directly and then use the invariant layer plus the closest honestly verified example in the same stack as a fallback.

| Language | Stack | Stack-specific acquisition files | Current posture | Closest verified fallback | Follow-on |
| --- | --- | --- | --- | --- | --- |
| Python | python-fastapi-uv-ruff-orjson-polars | none yet | invariant-layer-only | examples/canonical-api/fastapi-endpoint-example.py (behavior-verified) | PROMPT_34 |
| Go | go-echo | none yet | invariant-layer-only | examples/canonical-api/go-echo-handler-example.go (syntax-checked) | PROMPT_34 |
| Elixir | elixir-phoenix | none yet | invariant-layer-only | examples/canonical-api/phoenix-route-controller-example.ex (syntax-checked) | PROMPT_35 |
| Rust | rust-axum-modern | none yet | invariant-layer-only | examples/canonical-api/rust-axum-route-example.rs (syntax-checked) | PROMPT_34 |
| TypeScript | typescript-hono-bun | none yet | invariant-layer-only | examples/canonical-api/typescript-hono-handler-example.ts (syntax-checked) | PROMPT_34 |
| Nim | nim-jester-happyx | none yet | invariant-layer-only | examples/canonical-api/nim-jester-data-endpoint-example.nim (syntax-checked) | PROMPT_35 |
| Zig | zig-zap-jetzig | none yet | invariant-layer-only | examples/canonical-api/zig-zap-data-endpoint-example.zig (syntax-checked) | PROMPT_35 |
| Crystal | crystal-kemal-avram | none yet | invariant-layer-only | examples/canonical-api/crystal-kemal-avram-data-endpoint-example.cr (syntax-checked) | PROMPT_35 |

The machine-readable source for this table is `examples/canonical-data-acquisition/language-support-matrix.yaml`.

## Selection Contract

- doctrine and workflows are the generic layer
- stack-specific canonical examples are the preferred completed implementation layer
- a canonical acquisition example must be real code in the target stack
- verification depth can differ by language, but the level must match actual repository checks
- assistants should prefer the closest stack match with the highest honest verification level
- if no stack-matching acquisition example exists, assistants should say so and fall back to the invariant docs plus the closest verified fallback example in the same language
- if the user says not to give Python-only guidance, do not route through Python snippets by default

## Verification Posture

- this README is `syntax-checked` through structural validation
- `language-support-matrix.yaml` is `syntax-checked` and cross-checked against the verification registry and support matrix
- stack-specific acquisition implementations will be added in follow-on prompts and can only claim `syntax-checked`, `smoke-verified`, or `behavior-verified` when matching automation lands with them
