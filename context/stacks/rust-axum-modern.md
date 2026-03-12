# Rust: Axum

Use this pack for typed backend services where Rust performance or reliability matters.

## Typical Repo Surface

- `Cargo.toml`
- `src/main.rs`
- `src/http/`
- `src/domain/`
- `src/storage/`
- `tests/smoke/`
- `tests/integration/`

## Common Change Surfaces

- route trees
- extractors and response types
- shared app state
- background tasks
- storage and search adapters

## Testing Expectations

- smoke test boot plus one route through the router
- integration tests against real infra for storage, queue, or search boundaries
- prefer small focused tests over sprawling async harnesses

## Common Assistant Mistakes

- pushing all logic into `main.rs`
- overengineering trait layers before one real implementation exists
- replacing a needed integration test with mocked async code

