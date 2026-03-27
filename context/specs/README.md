# Spec Modules

These files are the canonical narrative modules used to compose repo-local `.acb/specs/*.md` payloads.

The structure is layered by the truth being expressed:

- `product/`: what the repo or system is meant to do
- `architecture/`: structural boundaries, allowed seams, and implementation constraints
- `agent/`: assistant operating rules, doctrine summaries, and router-aware work discipline
- `evolution/`: safe change-control and drift discipline

Within each layer:

- `base.md` applies everywhere
- `archetypes/` narrows by repo shape
- `stacks/` narrows by implementation surface where relevant
- `capabilities/` narrows by optional behavior such as APIs, workers, storage, or deployment
- `doctrine/` and `routers/` apply to agent behavior because they shape how sessions should operate

Generated repos should read the synthesized `.acb/specs/*.md` files first. These canonical modules exist so future tooling can recompose, diff, and audit those generated files.
