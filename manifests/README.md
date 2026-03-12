# Manifests

Manifests provide lightweight routing metadata for this base repo and for future repos derived from it.

## Manifest Types

- `repo.profile.yaml`: the active repo profile
- `profiles/*.yaml`: example or starter profiles for future repos

## Core Schema

Every profile should define:

- `schema_version`
- `kind`
- `name`
- `slug`
- `summary`
- `archetypes`
- `stacks`
- `required_context`
- `optional_context`
- `load_order`
- `trigger_words`
- `preferred_examples`
- `anti_patterns`
- `bootstrap_defaults`

## Infrastructure Defaults

Profiles should encode these invariants when relevant:

- Compose filenames stay `docker-compose.yml` and `docker-compose.test.yml`
- Compose `name:` values are repo-derived
- dev and test host ports use different explicit non-default bands
- test env files, data roots, volumes, fixtures, and seed/reset flows are isolated from dev

## Profile Naming

Use deterministic lowercase kebab-case names such as:

- `backend-api-fastapi-polars.yaml`
- `local-rag-base.yaml`
- `dokku-deployable-typescript-hono-bun.yaml`

Avoid vague names such as `default.yaml`, `service.yaml`, or `api2.yaml`.
