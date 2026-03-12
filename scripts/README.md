# Scripts

This directory contains lightweight repository utilities.

## `new_repo.py`

Bootstraps a new descendant repo from the base conventions.

Capabilities:

- choose an archetype and primary stack
- select or infer manifests
- optionally enable Dokku, prompt-first prompts, smoke tests, integration tests, and seed data
- generate isolated `docker-compose.yml` and `docker-compose.test.yml`
- generate `AGENT.md`, `CLAUDE.md`, `README.md`, `.gitignore`, and generated profile files

Examples:

```bash
python scripts/new_repo.py analytics-api \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data

python scripts/new_repo.py prompt-kit \
  --archetype prompt-first-repo \
  --primary-stack prompt-first-repo \
  --prompt-first
```

## `validate_manifests.py`

Checks that manifest files:

- exist under `manifests/`
- use the expected v2 keys
- reference files that actually exist
- keep `name` aligned with the filename
- keep stack, archetype, and support flags consistent

## `preview_context_bundle.py`

Accepts a manifest name or manifest path and prints the ordered context bundle that should be loaded first.

Examples:

```bash
python scripts/validate_manifests.py
python scripts/preview_context_bundle.py backend-api-fastapi-polars
python scripts/preview_context_bundle.py manifests/local-rag-base.yaml
python scripts/preview_context_bundle.py dokku-deployable-go-echo --show-templates
```

## `manifest_tools.py`

Shared parser and validator helpers used by the other scripts.

These scripts intentionally keep dependencies minimal and use a constrained YAML parser suited to the manifest schema in this repo.
