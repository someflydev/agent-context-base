# CLAUDE.md

Use this file as a routing entrypoint.

Start with:

1. `README.md`
2. `docs/repo-purpose.md`
3. `docs/repo-layout.md`
4. `manifests/project-profile.yaml`
5. `.generated-profile.yaml`

Then infer the smallest useful context bundle from the task, repo signals, and active change surface.

## Guardrails

- load one workflow first
- prefer one canonical example over several near-matches
- keep dev and test infrastructure isolated
- stop when stack, archetype, or Compose isolation becomes ambiguous
- keep prompt numbering monotonic when this repo stores prompt files
