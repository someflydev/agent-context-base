# Scripts

This directory contains lightweight repository utilities used during repo classification, generation, validation, and context inspection.

In the normal workflow, a coding assistant runs most of these scripts on your behalf while it is deciding how to generate a repo, checking what context to load, or verifying that the base remains internally consistent. Humans usually run them directly only when they want to inspect available options, validate repo health, or troubleshoot what the assistant is doing.

Common assistant-invoked scripts:

- `new_repo.py` to generate a new repo once the project shape and stack are clear
- `preview_context_bundle.py` to inspect which context should load first for a given manifest
- `prompt_first_repo_analyzer.py` to classify an existing repo by file signals
- `validate_manifests.py` and `validate_context.py` to verify the base after changes

Common human-invoked scripts:

- `new_repo.py --list-*` when you want to inspect available archetypes, stacks, or manifests yourself
- `validate_context.py` when you want a direct health check on the base
- `pattern_diff.py` when you want to compare a repo surface against an example or template manually

## `new_repo.py`

Bootstraps a new descendant repo from the base conventions.

This is usually invoked by the assistant after it has translated a short project description into an archetype, primary stack, and optional flags. Humans mainly run it directly when they already know the desired shape or want to inspect `--list-archetypes`, `--list-stacks`, or `--list-manifests`.

Capabilities:

- choose an archetype and primary stack
- optionally override or confirm storage and broker services explicitly
- select or infer manifests
- vendor selected base manifests under `manifests/base/` in the generated repo
- optionally enable Dokku, prompt-first prompts, smoke tests, integration tests, and seed data
- generate isolated `docker-compose.yml` and `docker-compose.test.yml`
- generate `AGENT.md`, `CLAUDE.md`, `.gitignore`, and generated profile files
- snapshot the operator prompt into `.prompts/initial-prompt.txt` when provided
- emit `.acb/generation-report.json` for generation auditability
- defer root `README.md` and broad root `docs/` by default unless you explicitly opt into them
- generate prompt-first orchestration repos from leaf derived examples or derived collections

Examples:

```bash
python scripts/new_repo.py analytics-api \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data \
  --initial-prompt-file /tmp/operator-brief.txt

python scripts/new_repo.py prompt-kit \
  --archetype prompt-first-repo \
  --primary-stack prompt-first-repo \
  --prompt-first

python scripts/new_repo.py --list-storage-services

python scripts/new_repo.py 047-go-python-ml-gateway \
  --use-example 47 \
  --storage-service postgres \
  --storage-service nats \
  --initial-prompt-file /tmp/ml-gateway-brief.txt \
  --target-dir /tmp/047-go-python-ml-gateway

python3 scripts/new_repo.py --derived-example ingestion-normalization-core --target-dir /tmp
python3 scripts/new_repo.py --derived-example team-a --target-dir /tmp
python3 scripts/new_repo.py --derived-example operator-surface --derived-context-mode maximal --target-dir /tmp
```

Derived generation notes:

- `--derived-example <leaf>` generates one prompt-first orchestration repo for that scenario
- `--derived-example team-a`, `team-b`, or `all-derived` generates one child repo per derived example
- `--derived-context-mode compact|maximal` controls how much prompt-first support context is vendored for derived repos; the default is `compact`
- when `--target-dir` points at `/tmp` or any existing directory, that directory is treated as the parent and each derived repo is written under it
- derived repos keep their repo-local summary in `.acb/manifests/project-profile.yaml` and vendor selected base manifests under `.acb/manifests/base/*.yaml`
- ordinary generated repos also reserve `.acb/` for generator audit artifacts such as `.acb/generation-report.json`
- `compact` and `maximal` both use the hidden `.acb/` container so only `AGENT.md` and `CLAUDE.md` remain as non-hidden root entrypoints
- `compact` vendors the selected manifests plus manifest-linked support assets into `.acb/`
- `maximal` uses the same `.acb/` root while adding a bounded local bundle of prompt-first anchors, startup/routing skills, canonical prompt/workflow examples, prompt-governance templates, and source-example archetype/stack docs
- new prompt-first generation writes `.prompts/` directly and does not generate `PROMPTS.md` by default
- leaf derived repos use `.prompts/PROMPT_01.txt` through `.prompts/PROMPT_04.txt` instead of the generic `001-...` prompt-first starter pair, and those prompts explicitly tell downstream assistants to use vendored manifests plus generated profiles as the local replacement for the base repo
- derived repos also record `.acb` root metadata, manifest-linked and maximal startup path lists, local canonical examples/workflows, and preferred startup order in generated profile metadata so a fresh assistant session can stay repo-local

## `init_memory.py`

Creates a repo-local `MEMORY.md` from the starter template if it is missing.

Assistants typically run this after the generated repo exists and the work is likely to span multiple sessions. Humans usually run it directly only when setting up continuity or repairing a repo that is missing its memory file.

Examples:

```bash
python scripts/init_memory.py
python scripts/init_memory.py --with-handoffs
python scripts/init_memory.py /tmp/example-repo --memory-path docs/MEMORY.md
```

## `create_handoff_snapshot.py`

Creates a timestamped handoff snapshot under `artifacts/handoffs/` by default.

Assistants use this when a task needs a durable checkpoint between sessions or before a risky branch of work. Humans usually run it directly when they want to force a clean handoff snapshot at a specific moment.

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

This is mainly a validation script for assistants or humans who want to confirm that continuity notes are still usable.

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

Assistants usually run this after editing manifests or templates. Humans typically run it when reviewing repo health or investigating generation issues.

## `validate_context.py`

Runs the broader integrity pass for the base itself:

- manifest validation
- context weighting, repo signal, and example catalog checks
- prompt numbering checks
- markdown cross-reference and Mermaid path checks
- bootstrap verification for Compose naming, port allocation, and environment isolation

This is the main verification entrypoint after documentation, manifest, template, or generator changes. Both assistants and humans use it, but it is especially useful as a direct human sanity check.

## `validate_doc_governance.py`

Runs the focused documentation-timing and freshness checks:

- broken markdown cross-references
- obviously stale Mermaid path references

Use this after changing docs, diagrams, templates, or generated bootstrap guidance.

## `preview_context_bundle.py`

Accepts a manifest name or manifest path and prints the ordered context bundle that should be loaded first.

Assistants use this to keep startup context small and explicit. Humans usually run it only when they want to inspect or challenge the assistant's context-loading choice.

## `prompt_first_repo_analyzer.py`

Infers likely stacks, archetypes, workflows, and manifests from the target repo's actual file signals.

This is most useful when the assistant is classifying an existing repo or checking whether a generated repo still matches its intended shape.

## `pattern_diff.py`

Shows a readable diff between two files or two directory trees so a repo surface can be compared against a canonical example or a template.

This is primarily an inspection and troubleshooting tool for either the assistant or the human reviewer.

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
scripts/smoke/new_repo_acb_smoke.sh
```

## `scripts/smoke/new_repo_acb_smoke.sh`

Runs a small derived-repo smoke matrix for the hidden `.acb/` layout.

- uses `/tmp/smoke-acb-<git-short-sha>/` as the parent output root
- uses `/tmp/smoke-acb-<YYYYMMDD-HHMMSS>-<git-short-sha>/` as the parent output root
- exercises `operator-surface` in `compact` and `maximal`
- exercises `team-a` in `compact` and `maximal`
- prints the root layout for a few generated repos so the hidden-container rule is easy to inspect

## `manifest_tools.py`

Shared parser and validator helpers used by the other scripts.

These scripts intentionally keep dependencies minimal and use a constrained YAML parser suited to the manifest schema in this repo.
