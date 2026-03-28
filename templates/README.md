# Templates

Templates are starter scaffolds for future repos derived from this base.

Use them when `scripts/new_repo.py` or a focused manual change needs a short, adaptable starting point.

## Boundary

- templates are not canonical examples
- templates should stay short and adaptable
- doctrine and examples still control the recommended pattern
- front-facing templates such as `templates/readme/README.template.md` are for repos that have earned those docs, not for speculative day-one prose

## Template Groups

- `agent-md/` and `claude-md/` for assistant entrypoints
- `readme/` for repo bootstrap documentation
- `manifest/` for generated profile files
- `gitignore/` for stack-aware ignore rules
- `compose/` for primary/dev and test Docker layouts
- `prompt-first/` for monotonic prompt-file starters
- `memory/` for legacy continuity starter scaffolds and handoff snapshots
- `smoke-tests/`, `integration-tests/`, and `seed-data/` for starter verification scripts
- `dokku/` for deployment notes

## Expected Use

1. choose the archetype, primary stack, and manifests
2. render the smallest useful template set
3. adapt the generated files to the project
4. validate the result against doctrine, manifests, and canonical examples
