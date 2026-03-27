---
acb_origin: canonical
acb_source_path: context/validation/stacks/go-echo.md
acb_role: validation
acb_stacks: [go-echo]
acb_version: 1
---

## Go/Echo Stack Validation

Use handler-level or request-level tests with explicit status and serialization assertions. Add real persistence proof when the changed path crosses the data boundary.

Typical commands:

- `go test ./...`
- `go test -tags integration ./tests/integration/...`
