# Deployment Readiness Checklists

Use these checklists before calling a repo deploy-ready.

## Baseline

- the active manifest still matches the repo shape
- `python scripts/validate_context.py` passes
- at least one smoke path proves boot or a representative happy path
- storage, queue, search, or release behavior has one minimal real boundary check when applicable
- `docker-compose.yml` and `docker-compose.test.yml` both declare explicit `name:`
- dev and test host ports are explicit and non-overlapping
- dev data and test data live under separate volume roots

## Dokku-Oriented Service

- `Procfile` contains explicit `web:` and `release:` commands
- `app.json` documents only real deploy-time env assumptions
- `docs/deployment.md` states required config, smoke target, and rollback posture
- post-deploy smoke stays small and fails loudly
- release or migration commands are documented and idempotent enough for repeated deploys

## Prompt-First Repo

- prompt filenames remain monotonic
- `PROMPTS.md` matches the real prompt set
- generated profile files still match the repo shape
- routing docs point to the smallest useful bundle instead of a full-repo dump

## Related Files

- `context/doctrine/deployment-philosophy-dokku.md`
- `context/doctrine/compose-port-and-data-isolation.md`
- `examples/canonical-dokku/README.md`
- `examples/canonical-observability/README.md`
