# CLAUDE.md

Use this file as the assistant boot entrypoint.

Start with:

1. `manifests/project-profile.yaml`
2. `.generated-profile.yaml`
3. `README.md` if it exists and still matches implemented reality
4. `docs/repo-purpose.md` if it exists
5. `docs/repo-layout.md` if it exists

After that stable pass and a narrow repo-signal check, read `MEMORY.md` if it exists.

Then load the smallest useful bundle from the task, repo signals, and active change surface.

When routing, selecting examples, assembling context bundles, choosing a verification path, or
reading and writing `MEMORY.md`, load the relevant skill from `context/skills/` rather than
relying on implicit judgment.

## Guardrails

- load one workflow first
- prefer one canonical example over several near-matches
- use `MEMORY.md` only as continuity state
- refresh `MEMORY.md` at meaningful stop points
- create a handoff snapshot when another session is likely
- keep root `README.md`, `docs/`, and Mermaid diagrams deferred until the repo has enough real structure to describe honestly
- keep dev and test infrastructure isolated
- `docker-compose.test.yml` is the only target for destructive test reset flows
- do not add GitHub Actions or CI workflows until explicitly asked
- stop when stack, archetype, or Compose isolation becomes ambiguous

## Running Commands

Tool environments are project-local. Never use system runtimes, global installs, or bare tool
names without an explicit path. See `context/doctrine/tool-invocation-discipline.md` in the
base repo for the full per-stack rules.

{{tool_invocation_notes}}

If `.venv_tools/` exists in the repo root, always invoke via `.venv_tools/bin/` paths.
Never activate the venv with `source` — always use the explicit binary path.
