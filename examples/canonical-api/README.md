# Canonical API Examples

Use this category for preferred route, handler, validation, and service-boundary examples.

Primary files in this category:

- `fastapi-endpoint-example.py`
- `typescript-hono-handler-example.ts`
- `rust-axum-route-example.rs`
- `go-echo-handler-example.go`
- `phoenix-route-controller-example.ex`
- `phoenix-router-surface-example.ex`

## A Strong Canonical API Example Should Show

- route registration shape
- request validation or decoding pattern
- separation between transport and domain logic
- representative error handling
- smoke-test shape for one route
- minimal real-infra integration-test shape when storage or search is involved

## Choosing This Example

Choose this category when the task is about adding or fixing endpoints, controllers, or handlers.

## Drift To Avoid

- framework-agnostic abstractions that hide the real route shape
- examples that imply smoke tests alone are enough for storage-backed routes
- controller-heavy patterns that bypass service or domain structure entirely
