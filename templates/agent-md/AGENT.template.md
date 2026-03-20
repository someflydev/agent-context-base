# AGENT.md

Purpose: boot the assistant into the smallest useful context bundle for this repo.

## First Reads

1. `{{repo_local_profile_path}}`
2. `{{generated_profile_path}}`
3. `{{vendored_base_manifests_dir}}/*.yaml` if present
4. `.prompts/*.txt` if present
5. `README.md` if it exists and still matches implemented reality
6. `{{repo_local_purpose_doc_path}}` if it exists
7. `{{repo_local_layout_doc_path}}` if it exists

After that stable pass and a narrow repo-signal check, read `MEMORY.md` if it exists.

When routing, selecting examples, assembling context bundles, choosing a verification path, or
reading and writing `MEMORY.md`, prefer the repo-local guidance vendored under
`{{vendored_base_root}}/context/`, `{{vendored_base_root}}/examples/`, and
`{{vendored_base_root}}/templates/` when those paths are present.

If `{{repo_local_profile_path}}` records `derived_metadata.derived_context_mode: maximal`,
the additional vendored bundle under `.acb/` is intentional. Use those repo-local copies as
the routing and prompt-continuation surface before assuming you need the source generator repo.

For derived repos, follow `derived_metadata.downstream_startup_order` in
`{{repo_local_profile_path}}`. If present, `derived_metadata.manifest_bundle_startup_paths`
and `derived_metadata.maximal_bundle_startup_paths` identify the vendored doctrine,
workflow, and canonical-example files that should be read before extending `.prompts/`.

## Repo Profile

- archetype: `{{archetype}}`
- primary stack: `{{primary_stack}}`
- selected manifests: `{{selected_manifests}}`
- repo-local profile path: `{{repo_local_profile_path}}`
- generated profile path: `{{generated_profile_path}}`
- vendored base manifests under `{{vendored_base_manifests_dir}}/` are the repo-local snapshots of base-repo intent when present

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
`{{repo_local_profile_path}}`, `{{generated_profile_path}}`, and any vendored
`{{vendored_base_root}}/context/`
guidance that exists in this repo.

{{tool_invocation_notes}}

If `.venv_tools/` exists in the repo root, always invoke via `.venv_tools/bin/` paths.
Never activate the venv with `source` — always use the explicit binary path.
