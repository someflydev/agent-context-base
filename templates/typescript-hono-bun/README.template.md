# TypeScript Hono Starter Notes

This starter assumes:

- Hono for request routing
- Bun for local execution
- Drizzle ORM for schema and query work
- TSX-capable route files when HTML fragments matter

Suggested layout:

- `src/index.ts`
- `src/routes/`
- `src/db/`
- `tests/smoke/`
- `tests/integration/`

Keep route handlers small and keep Drizzle changes under real integration coverage.

