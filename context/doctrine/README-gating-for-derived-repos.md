# README Gating For Derived Repos

Use this doctrine when deciding whether a derived repo should gain a root `README.md`.

## Goal

The root `README.md` should be a trustworthy front door. It should not exist only because generators and templates make it easy.

## Create The Root README Only When

- the repo has a real primary purpose that can be described in one or two honest paragraphs
- at least one implemented path or capability already exists
- the startup instructions point to real files and real commands
- any listed architecture components already exist in code or committed config
- the owner is willing to keep the file current

## Delay The Root README When

- the repo still contains mostly scaffolding
- routes, ingestion paths, storage choices, or worker boundaries are unsettled
- the text would mostly describe planned features
- the README would need diagrams to explain architecture that has not been implemented yet

## If A Minimal Root README Is Explicitly Requested

Keep it extremely small:

- name
- one-sentence current purpose
- pointer to `AGENT.md`, `CLAUDE.md`, or the generated profile
- one sentence stating that broader public docs are intentionally deferred until implementation stabilizes

Do not include architecture sections, roadmap prose, or aspirational diagrams in that version.

## Upgrade Trigger

Expand the root README after a meaningful implementation milestone, such as:

- a working ingestion path
- a committed parsing and normalization path
- a real database boundary
- event flow or sync behavior that can be described concretely
- backend behavior that has verification and stable entrypoints

## Related Workflow

- `context/workflows/decide-when-to-create-root-readme.md`
