# Scripts

This directory contains lightweight repository utilities.

## `validate_manifests.py`

Checks that manifest files:

- exist under `manifests/`
- use the expected v1 keys
- reference files that actually exist
- keep `name` aligned with the filename

## `preview_context_bundle.py`

Accepts a manifest name or manifest path and prints the ordered context bundle that should be loaded first.

Examples:

```bash
python scripts/validate_manifests.py
python scripts/preview_context_bundle.py backend-api-fastapi-polars
python scripts/preview_context_bundle.py manifests/local-rag-base.yaml
```

These scripts intentionally keep dependencies minimal and use a constrained YAML parser suited to the manifest schema in this repo.

