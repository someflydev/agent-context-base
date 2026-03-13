# Canonical API Examples

Use this category for preferred route, handler, validation, and service-boundary examples.

Primary files in this category:

- `fastapi-endpoint-example.py`
- `fastapi-example/app.py`
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
