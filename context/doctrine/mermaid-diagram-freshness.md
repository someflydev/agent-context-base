# Mermaid Diagram Freshness

Mermaid diagrams are useful only when they reflect implemented or committed architecture. In derived repos, stale diagrams are often more misleading than missing diagrams because they look authoritative while describing a system that no longer exists.

## Rule

Do not add a Mermaid diagram until the underlying structure is real enough to describe concretely.

## Good Inputs For A Diagram

- committed route or worker entrypoints
- real storage or queue boundaries
- implemented ingestion, parsing, sync, or event paths
- verified deployment or runtime topology

## Bad Inputs For A Diagram

- vague future architecture
- component names that do not exist in code yet
- arrows that represent intended flows rather than implemented ones
- copied diagram shells carried over from the base repo

## Freshness Pass

Whenever a Mermaid diagram already exists, review it after:

- adding or removing a major subsystem
- renaming directories, scripts, or docs it references
- changing runtime topology, deployment layout, or event flow
- replacing one architecture boundary with another

## Validation Posture

Automated validation can catch broken file references and obviously stale path names, but it cannot prove semantic freshness. Keep a manual checklist in the workflow and update the diagram in the same implementation pass whenever the architecture changed.

## Practical Rule

If the most honest diagram would mostly say "to be decided", do not create the diagram yet.

## Related Workflow

- `context/workflows/refresh-mermaid-diagrams.md`
- `context/workflows/perform-doc-freshness-pass.md`
