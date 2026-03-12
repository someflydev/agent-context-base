# Compose Port And Data Isolation

Docker-backed isolation is a real v1 requirement.

## Conventional Filenames

Use these filenames unless there is a strong reason not to:

- `docker-compose.yml`
- `docker-compose.test.yml`

Do not invent alternate top-level names for normal dev and test stacks.

## Compose `name:`

Set a repo-derived Compose `name:` value in each file so stacks from different repos can run side by side.

Recommended pattern:

- dev: `<repo-slug>`
- test: `<repo-slug>-test`

## Host Ports

- use explicit non-default host ports
- keep them documented in repo docs or env examples
- keep dev and test host ports distinct
- never assume one repo owns the default port for a shared service

Examples:

- PostgreSQL `55432` for dev and `56432` for test
- Redis `56379` for dev and `57379` for test
- Meilisearch `17700` for dev and `18700` for test

## Data Roots

Keep primary or dev data separate from test fixture data.

Recommended pattern:

- `docker/volumes/dev/...`
- `docker/volumes/test/...`

These paths should stay ignored by Git.

## Seed And Reset Boundaries

- dev seed commands may initialize local working data
- test seed commands may initialize disposable fixture data
- test reset commands must never touch dev data
- destructive reset operations should target test Compose services explicitly

## Why This Matters

The base repo assumes multiple local repos may run at once. Clear Compose names, explicit ports, and isolated data prevent accidental cross-repo contamination.

