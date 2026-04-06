# CLAUDE.md

Use this file as the assistant boot entrypoint.

Start with:

1. `{{repo_local_profile_path}}`
2. `{{generated_profile_path}}`
3. `.acb/SESSION_BOOT.md` if it exists
4. `.acb/profile/selection.json` if it exists
5. `.acb/specs/AGENT_RULES.md` and `.acb/specs/VALIDATION.md` if they exist
6. `.acb/validation/CHECKLIST.md` if it exists
7. `.acb/generation-report.json` if it exists
8. `{{vendored_base_manifests_dir}}/*.yaml` if present
9. `.prompts/*.txt` if present
10. `README.md` if it exists and still matches implemented reality
11. `{{repo_local_purpose_doc_path}}` if it exists
12. `{{repo_local_layout_doc_path}}` if it exists

After that stable pass:

1. run `python3 scripts/work.py resume` when the repo has a root `scripts/` directory
2. otherwise run `python3 .acb/scripts/work.py resume` in compact derived repos
3. read `context/TASK.md` if it exists
4. read `context/SESSION.md` if it exists
5. read `context/MEMORY.md` only if durable repo-local truths matter
6. read `PLAN.md` when milestone context matters
7. read `tmp/*.md` only when there is an active local markdown checkbox checklist or ad hoc session plan relevant to the task

Then load the smallest useful bundle from the task, repo signals, and active change surface.

Treat `{{vendored_base_manifests_dir}}/*.yaml` as the repo-local snapshots of base-repo routing and bootstrap intent when those files exist.

Treat the visible root as the active entrypoint and product working surface. Treat `.acb/` as the bounded
generator-owned assistant support bundle for this repo, not as a second public docs tree.

When present, use `.acb/manifests/base/` to recover generator intent, `.acb/context/` for doctrine and workflow
guidance, `.acb/examples/` for repo-local canonical references, `.acb/templates/` for extension/reference
templates, `.acb/specs/` for synthesized truth statements, `.acb/validation/` for proof obligations,
and `.acb/scripts/` for continuity helpers.

When routing, selecting examples, assembling context bundles, choosing a verification path, or
reading and writing `MEMORY.md`, prefer the repo-local guidance vendored under
`{{vendored_base_root}}/context/`, `{{vendored_base_root}}/examples/`, and
`{{vendored_base_root}}/templates/` when those paths are present.

If `ordinary_context_mode` is present in `{{repo_local_profile_path}}`, treat the listed
`manifest_bundle_startup_paths`, `repo_local_routing_model_paths`, `local_canonical_examples_available`,
`local_templates_available`, and `local_continuity_tools_available` fields as the explicit repo-local startup model.

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
- treat `PLAN.md`, `context/TASK.md`, `context/SESSION.md`, and `context/MEMORY.md` as repo-local runtime state
- keep `context/SESSION.md` concise and action-oriented
- keep `context/TASK.md` focused on the active slice
- keep `context/MEMORY.md` durable and clean
- keep prompt-session checklists or ad hoc work plans in `tmp/*.md`; use real markdown checkboxes (`- [ ]` / `- [x]`) for checklist items
- when `.acb/SESSION_BOOT.md` includes a `Context Tools` section, those commands are enabled for this repo; otherwise keep startup quiet
- if another session is likely and you create a handoff file, create `tmp/HANDOFF.md` and keep it local-only
- use `python3 scripts/work.py checkpoint` at meaningful stop points when the root script exists; otherwise use `python3 .acb/scripts/work.py checkpoint`
- if the repo adds `PLAN.example.md`, `context/TASK.example.md`, `context/SESSION.example.md`, or `context/MEMORY.example.md`, expect `init` and `checkpoint` to scaffold missing runtime files from those examples
- update `PLAN.md` only when a `.prompts` megaprompt or major decision materially reshapes phases or milestones
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
