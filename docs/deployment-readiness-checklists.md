# Deployment Readiness Checklists

Use these checks before calling a repo deploy-ready.

## Baseline

- the active manifest still matches the repo shape
- `python3 scripts/validate_context.py` passes if docs, manifests, examples, or templates changed
- at least one smoke path proves boot or a representative happy path
- real storage, queue, search, or release behavior has one minimal real-boundary check when applicable
- `docker-compose.yml` and `docker-compose.test.yml` declare explicit `name:`
- dev and test ports do not overlap
- dev and test data stay under separate volume roots

## Dokku-Oriented Service

- `Procfile` contains explicit `web:` and `release:` commands
- `app.json` documents only real deploy-time assumptions
- `docs/deployment.md` names config, smoke target, and rollback posture
- post-deploy smoke remains small and loud

See `context/doctrine/deployment-philosophy-dokku.md` for the full Dokku deployment doctrine.

## Prompt-First Repo

- `.prompts/` prompt files are monotonically numbered with no gaps
- generated profile files still describe the repo accurately
- routing docs still point to a small bundle instead of a broad dump

## CLI Tool

- binary builds cleanly (`go build`, `cargo build --release`, or equivalent)
- `--help` output matches the README usage section
- smoke test passes without a TTY (piped input, no interactive prompt fallback)
- `--version` output reflects the current release tag

## See Also

- `docs/ARCHITECTURE_MAP.md` — system overview, arc statuses, directory index
- `context/doctrine/deployment-philosophy-dokku.md` — Dokku deployment doctrine
