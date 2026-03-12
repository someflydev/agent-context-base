# Compose, Port, And Data Isolation

Purpose: enforce local infrastructure invariants.

Required rules:

- Keep filenames `docker-compose.yml` and `docker-compose.test.yml`.
- Set top-level Compose `name:` from the repo slug.
- Use `<repo-slug>` for the primary/dev stack.
- Use `<repo-slug>-test` for the test stack.
- Do not expose services on default host ports.
- Use explicit non-default host ports.
- Keep test host ports in a different band from dev.
- Use separate env files, volumes, fixture data, databases, indexes, and seed/reset flows for test.

Prevents:

- container-name collisions
- shared data across dev and test
- accidental test damage to dev data
