# AGENT.md

Purpose: boot the assistant into the smallest useful context bundle for this repo.

## First Reads

1. `manifests/project-profile.yaml`
2. `.generated-profile.yaml`
3. `manifests/base/*.yaml` if present
4. `.prompts/*.txt` if present
5. `README.md` if it exists and still matches implemented reality
6. `docs/repo-purpose.md` if it exists
7. `docs/repo-layout.md` if it exists

After that stable pass and a narrow repo-signal check, read `MEMORY.md` if it exists.

When routing, selecting examples, assembling context bundles, choosing a verification path, or
reading and writing `MEMORY.md`, prefer the repo-local guidance vendored under `context/`,
`examples/`, and `templates/` when those paths are present.

If `manifests/project-profile.yaml` records `derived_metadata.derived_context_mode: maximal`,
the additional vendored `context/`, `examples/`, and `templates/` paths are intentional.
Use those repo-local copies as the routing and prompt-continuation surface before assuming
you need the source generator repo.

## Repo Profile

- archetype: `{{archetype}}`
- primary stack: `{{primary_stack}}`
- selected manifests: `{{selected_manifests}}`
- vendored base manifests under `manifests/base/` are the repo-local snapshots of base-repo intent when present

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
names without an explicit path. Use the repo-local commands documented in
`manifests/project-profile.yaml`, `.generated-profile.yaml`, and any vendored `context/`
guidance that exists in this repo.

{{tool_invocation_notes}}

If `.venv_tools/` exists in the repo root, always invoke via `.venv_tools/bin/` paths.
Never activate the venv with `source` — always use the explicit binary path.
