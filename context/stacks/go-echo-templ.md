# Go Echo templ

Purpose: Go service stack with HTMX-friendly templ rendering.

Typical paths:

- `cmd/`
- `internal/http/`
- `internal/services/`
- `internal/views/`
- `tests/`

Conventions:

- handlers stay thin
- services own business logic
- templ components are reusable and explicit

Testing:

- handler tests and smoke tests
- real infra tests when storage or queues are involved
