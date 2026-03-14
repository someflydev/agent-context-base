# Canonical Data Acquisition

This directory is the shared entry point for canonical source acquisition examples and the invariant layer they build on.

Primary files in this category:

- `fastapi-source-sync-example.py`
- `go-echo-source-sync-example.go`
- `phoenix-source-sync-example.ex`
- `rust-axum-source-sync-example.rs`
- `typescript-hono-source-sync-example.ts`
- `nim-jester-source-sync-example.nim`
- `zig-zap-source-sync-example.zig`
- `crystal-kemal-source-sync-example.cr`
- `language-support-matrix.yaml`

## Capability Gap

`PROMPT_30` and `PROMPT_33` established the doctrine, workflow, and metadata contract for acquisition-heavy repos. The remaining gap was that the example layer still read as invariant-only, which made it harder to show how raw archival, replay, provenance, and sync boundaries should look in real stack-specific code.

This category now keeps those layers separate:

- doctrine and workflows remain the cross-language rule layer
- the files in this directory are the canonical stack-specific acquisition anchors
- verification depth differs by language, and the repo now records those differences explicitly instead of smoothing them over

## Coverage Overview

These four follow-on stacks matter because they broaden the acquisition layer without pretending they all have Python-level verification:

- Elixir is supported in the repo, but Phoenix still has light verification depth. A real controller-adjacent sync example makes the acquisition boundary visible without claiming compile or runtime coverage that does not exist.
- Nim, Zig, and Crystal already have runnable backend example infrastructure in `examples/canonical-api/`, so they are credible anchors for polyglot acquisition expansion even though the new sync surfaces remain source-verified only.
- Adding acquisition examples in these stacks proves the capability is not tied to the Python, Go, Rust, and TypeScript cluster. The invariant layer now has concrete implementations across BEAM, Nim, Zig, and Crystal surfaces as well.

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

The machine-readable source for this table is `examples/canonical-data-acquisition/language-support-matrix.yaml`.

| Language | Stack | Stack-specific acquisition files | Current posture | Closest verified fallback | Delivery prompt |
| --- | --- | --- | --- | --- | --- |
| Python | python-fastapi-uv-ruff-orjson-polars | fastapi-source-sync-example.py (behavior-verified) | behavior-verified | examples/canonical-api/fastapi-endpoint-example.py (behavior-verified) | PROMPT_34 |
| Go | go-echo | go-echo-source-sync-example.go (syntax-checked) | syntax-checked | examples/canonical-api/go-echo-handler-example.go (syntax-checked) | PROMPT_34 |
| Elixir | elixir-phoenix | phoenix-source-sync-example.ex (structure-verified) | structure-verified | examples/canonical-api/phoenix-route-controller-example.ex (structure-verified) | PROMPT_35 |
| Rust | rust-axum-modern | rust-axum-source-sync-example.rs (syntax-checked) | syntax-checked | examples/canonical-api/rust-axum-route-example.rs (syntax-checked) | PROMPT_34 |
| TypeScript | typescript-hono-bun | typescript-hono-source-sync-example.ts (syntax-checked) | syntax-checked | examples/canonical-api/typescript-hono-handler-example.ts (syntax-checked) | PROMPT_34 |
| Nim | nim-jester-happyx | nim-jester-source-sync-example.nim (structure-verified) | structure-verified | examples/canonical-api/nim-jester-data-endpoint-example.nim (structure-verified) | PROMPT_35 |
| Zig | zig-zap-jetzig | zig-zap-source-sync-example.zig (structure-verified) | structure-verified | examples/canonical-api/zig-zap-data-endpoint-example.zig (structure-verified) | PROMPT_35 |
| Crystal | crystal-kemal-avram | crystal-kemal-source-sync-example.cr (structure-verified) | structure-verified | examples/canonical-api/crystal-kemal-avram-data-endpoint-example.cr (structure-verified) | PROMPT_35 |

Coverage notes:

- `fastapi-source-sync-example.py` is real code and `behavior-verified` through direct Python tests that prove raw capture, replay from archived payloads, provenance retention, and retry behavior.
- `go-echo-source-sync-example.go` is real code and `syntax-checked` through `gofmt` plus structure assertions. It does not have a native compile or runtime sync harness yet.
- `rust-axum-source-sync-example.rs` is real code and `syntax-checked` through `rustfmt --check` plus structure assertions. It does not have a native compile or runtime sync harness yet.
- `typescript-hono-source-sync-example.ts` is real code and `syntax-checked` through local `tsc` using Hono and Bun ambient shims. That proves parse and compile shape only; it does not prove Bun runtime behavior.
- `phoenix-source-sync-example.ex` is a real Elixir example, `structure-verified` only. Phoenix acquisition coverage does not yet include native parse, compile, or runtime checks.
- `nim-jester-source-sync-example.nim` is a real Nim example, `structure-verified` only. The existing Nim Docker-backed runtime bundle remains an API-surface anchor, not an acquisition harness.
- `zig-zap-source-sync-example.zig` is a real Zig example, `structure-verified` only. A Docker-backed runtime was not added for this acquisition surface.
- `crystal-kemal-source-sync-example.cr` is a real Crystal example, `structure-verified` only. Registry confidence remains medium because the new sync surface is not compile- or runtime-verified.

## Shared Semantic Contract

Across the stack-specific examples, the same semantic boundaries stay visible:

- raw archive paths are explicit and deterministic by source, repo, and fetch time
- normalized records carry provenance including source name, raw path, fetched time, checksum, and checkpoint token
- fetch, archive, parse, normalize, and sync entrypoint responsibilities stay legible
- replay runs can normalize from archived raw material without calling the upstream again
- source adapters stay narrow and source-specific instead of leaking upstream field oddities into canonical models
- retry or resume semantics stay attached to sync cursors and acquisition services rather than UI-facing response code

## Selection Contract

- doctrine and workflows are the generic layer
- stack-specific canonical examples are the preferred completed implementation layer
- a canonical acquisition example must be real code in the target stack
- assistants should prefer the closest stack-matching acquisition example with the highest honest verification level
- when a stack-specific acquisition example exists, use it before falling back to a non-acquisition example in the same language
- when no stack-specific acquisition example exists, say so directly and fall back to the invariant docs plus the closest verified example in the same stack
- if the user says not to give Python-only guidance, do not route through Python examples when a stack-matching acquisition example exists elsewhere

## Verification Posture

- this README is `structure-verified` through structural validation
- `language-support-matrix.yaml` is `syntax-checked` and cross-checked against the verification registry and support matrix
- `fastapi-source-sync-example.py` is `behavior-verified` by `verification/examples/python/test_fastapi_examples.py`
- `go-echo-source-sync-example.go` is `syntax-checked` by `verification/examples/go/test_echo_examples.py`
- `phoenix-source-sync-example.ex` is `structure-verified` by `verification/examples/elixir/test_phoenix_examples.py`
- `rust-axum-source-sync-example.rs` is `syntax-checked` by `verification/examples/rust/test_axum_examples.py`
- `typescript-hono-source-sync-example.ts` is `syntax-checked` by `verification/examples/typescript/test_hono_data_acquisition_examples.py`
- `nim-jester-source-sync-example.nim` is `structure-verified` by `verification/examples/nim/test_nim_jester_happyx_examples.py`
- `zig-zap-source-sync-example.zig` is `structure-verified` by `verification/examples/zig/test_zig_zap_jetzig_examples.py`
- `crystal-kemal-source-sync-example.cr` is `structure-verified` by `verification/examples/crystal/test_crystal_kemal_avram_examples.py`
- verification differences are intentional: Python is still the strongest acquisition example, Go, Rust, and TypeScript have parse-aware checks, and Elixir, Nim, Zig, and Crystal currently stop at honest structure coverage
