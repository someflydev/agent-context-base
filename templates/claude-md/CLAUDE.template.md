# CLAUDE.md

Use this file as the assistant boot entrypoint.

Start with:

1. `manifests/project-profile.yaml`
2. `.generated-profile.yaml`
3. `manifests/base/*.yaml` if present
4. `.prompts/*.txt` if present
5. `README.md` if it exists and still matches implemented reality
6. `docs/repo-purpose.md` if it exists
7. `docs/repo-layout.md` if it exists

After that stable pass and a narrow repo-signal check, read `MEMORY.md` if it exists.

Then load the smallest useful bundle from the task, repo signals, and active change surface.

Treat `manifests/base/*.yaml` as the repo-local snapshots of base-repo routing and bootstrap intent when those files exist.

When routing, selecting examples, assembling context bundles, choosing a verification path, or
reading and writing `MEMORY.md`, prefer the repo-local guidance vendored under `context/`,
`examples/`, and `templates/` when those paths are present.

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
names without an explicit path. Use the repo-local commands documented in
`manifests/project-profile.yaml`, `.generated-profile.yaml`, and any vendored `context/`
guidance that exists in this repo.

{{tool_invocation_notes}}

If `.venv_tools/` exists in the repo root, always invoke via `.venv_tools/bin/` paths.
Never activate the venv with `source` — always use the explicit binary path.
