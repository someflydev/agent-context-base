# CLAUDE.md

Use this file as the assistant boot entrypoint.

Start with:

1. `README.md`
2. `docs/repo-purpose.md`
3. `docs/repo-layout.md`
4. `manifests/project-profile.yaml`
5. `.generated-profile.yaml`

After that stable pass and a narrow repo-signal check, read `MEMORY.md` if it exists.

Then load the smallest useful bundle from the task, repo signals, and active change surface.

## Guardrails

- load one workflow first
- prefer one canonical example over several near-matches
- use `MEMORY.md` only as continuity state
- refresh `MEMORY.md` at meaningful stop points
- create a handoff snapshot when another session is likely
- keep dev and test infrastructure isolated
- stop when stack, archetype, or Compose isolation becomes ambiguous
