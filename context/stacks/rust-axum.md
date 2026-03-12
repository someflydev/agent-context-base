# Rust Axum

Purpose: typed Rust service stack for APIs and small web backends.

Typical paths:

- `src/routes/`
- `src/services/`
- `src/state/`
- `tests/`

Conventions:

- use explicit extractors and shared state
- keep route wiring separate from service logic

Testing:

- cargo unit tests
- infra-backed integration tests for external dependencies
