# Bootstrap Repo

Use this workflow when creating a new project repo from this base.

## Preconditions

- the target archetype is chosen
- the likely primary stack is chosen
- deployment posture is at least roughly known

## Sequence

1. choose the manifest closest to the target repo
2. copy only the relevant router, doctrine, workflow, stack, example, and template files
3. create project-local manifests and examples
4. wire `AGENT.md`, `CLAUDE.md`, README, and stack basics
5. define Docker-backed dev and test isolation
6. add smoke tests and any minimal real-infra integration tests required by the first significant feature

## Outputs

- a focused descendant repo, not a wholesale clone
- project-local routing and manifests
- initial test and deployment posture

## Related Docs

- `context/archetypes/prompt-first-repo.md`
- `context/doctrine/compose-port-and-data-isolation.md`
- `context/doctrine/deployment-philosophy-dokku.md`

## Common Pitfalls

- copying every file from the base without pruning
- leaving examples and templates indistinguishable
- delaying dev versus test isolation until later

