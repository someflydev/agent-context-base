# Decide When To Create Root README

Use this workflow when a derived repo does not yet have a root `README.md` or when someone asks whether it is time to add one.

## Goal

Create the root README only when it can describe implemented reality instead of intention.

## Sequence

1. inspect the implemented entrypoints, tests, manifests, and any operating scripts
2. confirm at least one meaningful end-to-end slice already exists
3. check whether startup guidance can point to real files and commands
4. reject speculative architecture prose, roadmap sections, and diagram shells
5. decide between:
   - defer the README
   - write a minimal factual README
   - write a fuller README because the repo has clearly earned it

## A Minimal Acceptable README Usually Contains

- repo name
- current implemented purpose
- one or two real startup or verification commands
- pointers to assistant boot docs or generated profile files
- a short note that broader docs were intentionally delayed until implementation stabilized

## Delay Signals

- mostly scaffolding and placeholders
- unstable architecture or directory layout
- missing verification for the main path
- diagrams would need to explain systems that do not exist yet

## Outputs

- a defer decision with rationale
- or a concise README that describes only implemented reality

## Related Doctrine

- `context/doctrine/documentation-timing-discipline.md`
- `context/doctrine/README-gating-for-derived-repos.md`
