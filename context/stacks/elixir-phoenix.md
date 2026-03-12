# Elixir: Phoenix

Use this pack for Phoenix web apps and services where Elixir concurrency and LiveView-friendly patterns are relevant.

## Typical Repo Surface

- `mix.exs`
- `lib/<app>/application.ex`
- `lib/<app>_web/router.ex`
- `lib/<app>_web/controllers/`
- `lib/<app>/`
- `priv/repo/migrations/`
- `test/`

## Common Change Surfaces

- Phoenix router and pipeline changes
- controller or LiveView entrypoints
- context modules
- Ecto schemas and queries
- release and runtime config

## Testing Expectations

- smoke test boot and one representative web path
- integration tests against isolated PostgreSQL or other real dependencies when persistence behavior changes
- include migration-path verification when schema changes matter

## Common Assistant Mistakes

- stuffing domain logic into controllers
- treating Ecto-backed changes as smoke-test-only work
- ignoring release and runtime config when deployment support is added

