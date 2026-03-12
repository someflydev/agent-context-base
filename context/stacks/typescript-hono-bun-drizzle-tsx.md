# TypeScript Hono Bun Drizzle TSX

Purpose: lightweight TypeScript backend and server-rendered fragment stack.

Typical paths:

- `src/routes/`
- `src/services/`
- `src/db/`
- `src/views/`
- `tests/`

Conventions:

- keep Hono route modules small
- let Drizzle schema and migrations stay authoritative
- use TSX for server-rendered fragments

Testing:

- smoke route tests
- real infra tests for DB/search/queue behavior
