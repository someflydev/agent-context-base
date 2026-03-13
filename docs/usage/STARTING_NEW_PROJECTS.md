# Starting New Projects

Use this base in two phases:

1. classify and generate in `agent-context-base`
2. build the product in the generated repo

## The Two-Repo Model

`agent-context-base` is the planning and generation repo. It helps you choose the project shape, stack, manifests, and starter assets.

The generated repo is the product repo. That is where the real application code, repo-local examples, and project-specific verification should live.

## From Idea To Generated Repo

1. Describe the project in plain language.
2. Choose one primary archetype.
3. Choose one primary stack.
4. Inspect the likely manifest bundle.
5. Generate the repo.

Useful commands:

```bash
python scripts/new_repo.py --list-archetypes
python scripts/new_repo.py --list-stacks
python scripts/new_repo.py --list-manifests
python scripts/preview_context_bundle.py backend-api-fastapi-polars --show-weights --show-anchors
```

Example:

```bash
python scripts/new_repo.py analytics-api \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data \
  --dokku
```

## What `new_repo.py` Actually Does

- picks the requested archetype and primary stack
- selects default manifests for that repo shape
- renders README, `AGENT.md`, `CLAUDE.md`, and generated profile files
- optionally renders prompt files, seed data, smoke tests, integration tests, and Dokku assets
- generates isolated `docker-compose.yml` and `docker-compose.test.yml` when the profile implies local infra

## First Steps In The Generated Repo

1. Start a fresh assistant session in the new repo.
2. Follow that repo's `AGENT.md` or `CLAUDE.md`.
3. Read the generated project profile and one matching canonical example.
4. Implement one vertical slice.
5. Verify it before expanding scope.
6. Create or update `MEMORY.md` if the work will continue later.

## Rules That Keep New Repos Clean

- pick one archetype first; do not start with a composite repo unless the product truly needs it
- pick one stack first; add more stacks only when the product boundary requires them
- keep examples and templates distinct
- let manifests and generated profiles narrow the first working set
- avoid carrying speculative future dependencies into the initial repo

See `docs/usage/ADVANCED_ASSISTANT_OPERATIONS.md` for longer-lived sessions after the generated repo exists.
