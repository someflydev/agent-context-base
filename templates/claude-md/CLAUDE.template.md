# CLAUDE.md

Use this file as the assistant boot entrypoint.

Start with:

1. `{{repo_local_profile_path}}`
2. `{{generated_profile_path}}`
3. `.acb/generation-report.json` if it exists
4. `{{vendored_base_manifests_dir}}/*.yaml` if present
5. `.prompts/*.txt` if present
6. `README.md` if it exists and still matches implemented reality
7. `{{repo_local_purpose_doc_path}}` if it exists
8. `{{repo_local_layout_doc_path}}` if it exists

After that stable pass and a narrow repo-signal check, read `MEMORY.md` if it exists.

Then load the smallest useful bundle from the task, repo signals, and active change surface.

Treat `{{vendored_base_manifests_dir}}/*.yaml` as the repo-local snapshots of base-repo routing and bootstrap intent when those files exist.

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
`{{repo_local_profile_path}}`, `{{generated_profile_path}}`, and any vendored
`{{vendored_base_root}}/context/`
guidance that exists in this repo.

{{tool_invocation_notes}}

If `.venv_tools/` exists in the repo root, always invoke via `.venv_tools/bin/` paths.
Never activate the venv with `source` — always use the explicit binary path.
