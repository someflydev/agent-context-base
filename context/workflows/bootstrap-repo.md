# Bootstrap Repo

Use this workflow when creating a new project repo from this base.

## Preconditions

- the target archetype is chosen
- the likely primary stack is chosen
- deployment posture is at least roughly known

## Sequence

1. choose the manifest closest to the target repo
2. copy only the relevant router, doctrine, workflow, skill, stack, example, and template files
3. create project-local manifests and examples
4. wire `AGENT.md`, `CLAUDE.md`, the generated profile, and stack basics
5. defer a substantial root `README.md` and root `docs/` until implementation has real structure
6. define Docker-backed dev and test isolation
7. add smoke tests and any minimal real-infra integration tests required by the first significant feature

## Outputs

- a focused descendant repo, not a wholesale clone
- project-local routing and manifests
- initial test and deployment posture

Note: the `context/skills/` directory is copied in full because skills describe cognitive procedures that apply in any derived repo, not base-repo-specific logic.

## Related Docs

- `context/archetypes/prompt-first-repo.md`
- `context/doctrine/compose-port-and-data-isolation.md`
- `context/doctrine/deployment-philosophy-dokku.md`
- `context/doctrine/documentation-timing-discipline.md`
- `context/skills/` — cognitive procedures carried into the derived repo for routing, selection, bundle assembly, and continuity

## Common Pitfalls

- copying every file from the base without pruning
- leaving examples and templates indistinguishable
- creating front-facing docs before the repo has real implementation to describe
- delaying dev versus test isolation until later
