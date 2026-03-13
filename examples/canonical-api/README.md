# Canonical API Examples

Use this category for preferred route, handler, validation, and service-boundary examples.

Primary files in this category:

- `fastapi-endpoint-example.py`
- `fastapi-example/app.py`
- `nim-jester-json-endpoint-example.nim`
- `nim-happyx-html-fragment-example.nim`
- `nim-jester-data-endpoint-example.nim`
- `nim-jester-happyx-example/main.nim`
- `scala-tapir-http4s-zio-api-endpoint-example.scala`
- `scala-tapir-http4s-zio-html-fragment-example.scala`
- `scala-tapir-http4s-zio-data-endpoint-example.scala`
- `scala-tapir-http4s-zio-example/src/main/scala/Main.scala`
- `zig-zap-json-endpoint-example.zig`
- `zig-jetzig-html-fragment-example.zig`
- `zig-zap-data-endpoint-example.zig`
- `zig-zap-jetzig-example/main.zig`
- `typescript-hono-handler-example.ts`
- `rust-axum-route-example.rs`
- `rust-axum-example/src/main.rs`
- `go-echo-handler-example.go`
- `go-echo-example/main.go`
- `phoenix-route-controller-example.ex`
- `phoenix-router-surface-example.ex`

## Verification Metadata

- `fastapi-endpoint-example.py`
  Verification level: behavior-verified
  Harness: fastapi_min_app
  Last verified by: verification/examples/python/test_fastapi_examples.py
- `fastapi-example/app.py`
  Verification level: smoke-verified
  Harness: fastapi_min_app
  Last verified by: verification/examples/python/test_fastapi_examples.py
- `nim-jester-json-endpoint-example.nim`
  Verification level: syntax-checked
  Harness: nim_jester_happyx_min_app
  Last verified by: verification/examples/nim/test_nim_jester_happyx_examples.py
- `nim-happyx-html-fragment-example.nim`
  Verification level: syntax-checked
  Harness: nim_jester_happyx_min_app
  Last verified by: verification/examples/nim/test_nim_jester_happyx_examples.py
- `nim-jester-data-endpoint-example.nim`
  Verification level: syntax-checked
  Harness: nim_jester_happyx_min_app
  Last verified by: verification/examples/nim/test_nim_jester_happyx_examples.py
- `nim-jester-happyx-example/main.nim`
  Verification level: smoke-verified
  Harness: nim_jester_happyx_min_app
  Last verified by: verification/examples/nim/test_nim_jester_happyx_examples.py
- `scala-tapir-http4s-zio-api-endpoint-example.scala`
  Verification level: syntax-checked
  Harness: scala_tapir_http4s_zio_min_app
  Last verified by: verification/examples/scala/test_scala_tapir_http4s_zio_examples.py
- `scala-tapir-http4s-zio-html-fragment-example.scala`
  Verification level: syntax-checked
  Harness: scala_tapir_http4s_zio_min_app
  Last verified by: verification/examples/scala/test_scala_tapir_http4s_zio_examples.py
- `scala-tapir-http4s-zio-data-endpoint-example.scala`
  Verification level: syntax-checked
  Harness: scala_tapir_http4s_zio_min_app
  Last verified by: verification/examples/scala/test_scala_tapir_http4s_zio_examples.py
- `scala-tapir-http4s-zio-example/src/main/scala/Main.scala`
  Verification level: smoke-verified
  Harness: scala_tapir_http4s_zio_min_app
  Last verified by: verification/examples/scala/test_scala_tapir_http4s_zio_examples.py
- `zig-zap-json-endpoint-example.zig`
  Verification level: syntax-checked
  Harness: zig_zap_jetzig_min_app
  Last verified by: verification/examples/zig/test_zig_zap_jetzig_examples.py
- `zig-jetzig-html-fragment-example.zig`
  Verification level: syntax-checked
  Harness: zig_zap_jetzig_min_app
  Last verified by: verification/examples/zig/test_zig_zap_jetzig_examples.py
- `zig-zap-data-endpoint-example.zig`
  Verification level: syntax-checked
  Harness: zig_zap_jetzig_min_app
  Last verified by: verification/examples/zig/test_zig_zap_jetzig_examples.py
- `zig-zap-jetzig-example/main.zig`
  Verification level: smoke-verified
  Harness: zig_zap_jetzig_min_app
  Last verified by: verification/examples/zig/test_zig_zap_jetzig_examples.py
- `go-echo-handler-example.go`
  Verification level: syntax-checked
  Harness: go_echo_min_app
  Last verified by: verification/examples/go/test_echo_examples.py
- `go-echo-example/main.go`
  Verification level: smoke-verified
  Harness: go_echo_min_app
  Last verified by: verification/examples/go/test_echo_examples.py
- `rust-axum-route-example.rs`
  Verification level: syntax-checked
  Harness: rust_axum_min_app
  Last verified by: verification/examples/rust/test_axum_examples.py
- `rust-axum-example/src/main.rs`
  Verification level: smoke-verified
  Harness: rust_axum_min_app
  Last verified by: verification/examples/rust/test_axum_examples.py
- `phoenix-route-controller-example.ex`
  Verification level: syntax-checked
  Harness: none
  Last verified by: verification/examples/elixir/test_phoenix_examples.py
- `phoenix-router-surface-example.ex`
  Verification level: syntax-checked
  Harness: none
  Last verified by: verification/examples/elixir/test_phoenix_examples.py

## A Strong Canonical API Example Should Show

- route registration shape
- request validation or decoding pattern
- separation between transport and domain logic
- representative error handling
- smoke-test shape for one route
- minimal real-infra integration-test shape when storage or search is involved

## Choosing This Example

Choose this category when the task is about adding or fixing endpoints, controllers, or handlers. Prefer the highest verified example that matches the active stack.

## Drift To Avoid

- framework-agnostic abstractions that hide the real route shape
- examples that imply smoke tests alone are enough for storage-backed routes
- controller-heavy patterns that bypass service or domain structure entirely
