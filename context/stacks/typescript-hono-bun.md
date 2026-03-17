# TypeScript: Hono + Bun + Drizzle ORM + TSX

Use this pack for fast lightweight backend services, especially small HTMX, Tailwind, or Plotly-oriented apps and APIs.

## Typical Repo Surface

- `package.json`
- `bun.lockb` or `bun.lock`
- `tsconfig.json`
- `src/index.ts`
- `src/routes/`
- `src/lib/db.ts`
- `src/db/schema.ts`
- `src/db/migrations/`
- `tests/smoke/`
- `tests/integration/`

## Common Change Surfaces

- Hono route registration
- request validation
- Drizzle schemas and queries
- TSX-powered dev entrypoints or utilities
- server-rendered fragments for HTMX-oriented apps

## Testing Expectations

- smoke test boot and one representative Hono route
- real-infra integration tests when Drizzle touches PostgreSQL, SQLite, or another real database
- if HTMX responses are part of the contract, test response fragments, not just status codes

## Tool Setup

One-time setup:

```bash
bun install
bunx playwright install chromium    # only if the project uses Playwright
```

Running tests:

```bash
bun test                            # Bun's built-in test runner (unit and integration)
bun run test:e2e                    # project-defined e2e script
bunx playwright test                # direct Playwright invocation
```

Never use `npm install`, `npx`, or bare `node` in a Bun repo. Always use `bun` or `bunx`.
See `context/doctrine/tool-invocation-discipline.md`.

## Common Assistant Mistakes

- defaulting to Express patterns
- hiding SQL behavior behind untested abstractions
- treating Drizzle schema changes as docs-only work
- skipping real DB tests when migrations change behavior

