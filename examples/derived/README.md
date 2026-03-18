# examples/derived

This directory contains two derived content files used by the coverage verification layer.

## example-prompts.yaml

One hundred natural-language project briefs (2–4 sentences each), one per reference
project in `EXAMPLE_PROJECTS` in `scripts/new_repo.py`. Each entry includes a `codename`
matching the slug used in `EXAMPLE_PROJECTS`, the project's category, and a `new_repo_args`
block that mirrors the flags used to scaffold that project with `scripts/new_repo.py`.

These briefs serve as the human-readable input side of the coverage verification layer
(see PROMPT_77): a verifier can take a brief, call `new_repo.py --use-example <N>`, and
confirm the generated repo matches the intent described in the prompt.

## derived-examples.yaml

Eight sub-group "derived example" prompts (7–12 sentences each), organized into two teams
of four. Each entry synthesizes a cluster of 2–3 individual example projects into a coherent
multi-service scenario, describing how the component services interact and what seam contracts
connect them.

Team A — Intelligent Data Platform covers ingestion, analytics, ML routing, and operator
tooling. Team B — ML-Powered Observability covers event-driven coordination, search and
inference, time-series acquisition, and operational quality tooling.

## Usage by the coverage verification layer (PROMPT_77)

PROMPT_77 uses both files to verify coverage across archetypes, stacks, and categories.
The `example-prompts.yaml` entries serve as individual test cases; the `derived-examples.yaml`
entries serve as integration-level test cases spanning multiple archetypes and stacks.

## Authoring constraint

Prompt text in both files must not be modified without also updating the corresponding
`new_repo_args` block. The `new_repo_args` values are the authoritative record of how to
scaffold each project; the prompt text describes the intent. If they diverge, the
`new_repo_args` block takes precedence for verification purposes.
