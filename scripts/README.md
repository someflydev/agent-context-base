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

## `init_memory.py`

Creates a repo-local `MEMORY.md` from the starter template if it is missing.

It can also create a default handoff directory for longer-running tasks.

Examples:

```bash
python scripts/init_memory.py
python scripts/init_memory.py --with-handoffs
python scripts/init_memory.py /tmp/example-repo --memory-path docs/MEMORY.md
```

## `create_handoff_snapshot.py`

Creates a timestamped handoff snapshot under `artifacts/handoffs/` by default.

It can carry forward current state from `MEMORY.md` and accepts explicit flags for checkpoint details.

Examples:

```bash
python scripts/create_handoff_snapshot.py --title "memory-layer-pass" --from-memory
python scripts/create_handoff_snapshot.py \
  --title "prompt-batch-003" \
  --from-memory \
  --completed "wrote memory docs" \
  --remaining "wire AGENT.md and CLAUDE.md" \
  --next-file AGENT.md \
  --next-file CLAUDE.md
```

## `check_memory_freshness.py`

Warns when `MEMORY.md` is missing key sections, looks stale, still contains placeholders, or has grown beyond the intended high-signal size.

Examples:

```bash
python scripts/check_memory_freshness.py
python scripts/check_memory_freshness.py --strict
python scripts/check_memory_freshness.py /tmp/example-repo --max-age-hours 24
```

## `validate_manifests.py`

Checks that manifest files:

- exist under `manifests/`
- use the expected v2 keys
- reference files that actually exist
- keep `name` aligned with the filename
- keep stack, archetype, and support flags consistent

## `validate_context.py`

Runs the broader integrity pass for the base itself:

- manifest validation
- context weighting, repo signal, and example catalog checks
- prompt numbering checks
- bootstrap verification for Compose naming, port allocation, and environment isolation

## `preview_context_bundle.py`

Accepts a manifest name or manifest path and prints the ordered context bundle that should be loaded first.

It can also show context weights, assistant anchors, ranked examples, and repo-signal comparisons.

## `prompt_first_repo_analyzer.py`

Infers likely stacks, archetypes, workflows, and manifests from the target repo's actual file signals.

## `pattern_diff.py`

Shows a readable diff between two files or two directory trees so a repo surface can be compared against a canonical example or a template.

Examples:

```bash
python scripts/validate_manifests.py
python scripts/init_memory.py --with-handoffs
python scripts/create_handoff_snapshot.py --title "routing-pass" --from-memory
python scripts/check_memory_freshness.py --strict
python scripts/validate_context.py
python scripts/preview_context_bundle.py backend-api-fastapi-polars
python scripts/preview_context_bundle.py manifests/local-rag-base.yaml --show-weights --show-anchors
python scripts/preview_context_bundle.py dokku-deployable-go-echo --show-templates
python scripts/prompt_first_repo_analyzer.py .
python scripts/pattern_diff.py examples/canonical-api examples/canonical-smoke-tests
```

## `manifest_tools.py`

Shared parser and validator helpers used by the other scripts.

These scripts intentionally keep dependencies minimal and use a constrained YAML parser suited to the manifest schema in this repo.
