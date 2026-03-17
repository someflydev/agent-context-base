# AGENT.md

Purpose: boot the assistant into the smallest useful context bundle for this repo.

## First Reads

1. `manifests/project-profile.yaml`
2. `.generated-profile.yaml`
3. `README.md` if it exists and still matches implemented reality
4. `docs/repo-purpose.md` if it exists
5. `docs/repo-layout.md` if it exists

After that stable pass and a narrow repo-signal check, read `MEMORY.md` if it exists.

When routing, selecting examples, assembling context bundles, choosing a verification path, or
reading and writing `MEMORY.md`, load the relevant skill from `context/skills/` rather than
relying on implicit judgment.

## Repo Profile

- archetype: `{{archetype}}`
- primary stack: `{{primary_stack}}`
- selected manifests: `{{selected_manifests}}`

## Bundle Discipline

Load only:

1. the relevant doctrine
2. one workflow
3. the active stack or archetype guidance
4. one canonical example

## Guardrails

- keep this file concise
- treat `MEMORY.md` as continuity only
- update `MEMORY.md` at meaningful stop points
- create a handoff snapshot when another session is likely
- do not create a substantial root `README.md` or root `docs/` too early; wait until implementation can support them honestly
- stop when stack, archetype, or Compose isolation ambiguity would cause context sprawl
- `docker-compose.test.yml` is the only target for destructive test reset flows
- do not add GitHub Actions or CI workflows until explicitly asked

## Running Commands

Tool environments are project-local. Never use system runtimes, global installs, or bare tool
names without an explicit path. See `context/doctrine/tool-invocation-discipline.md` in the
base repo for the full per-stack rules.

{{tool_invocation_notes}}

If `.venv_tools/` exists in the repo root, always invoke via `.venv_tools/bin/` paths.
Never activate the venv with `source` — always use the explicit binary path.
