# Refresh Mermaid Diagrams

Use this workflow when a repo already has Mermaid diagrams and implementation changes may have made them stale.

## Goal

Keep diagrams aligned with real repo structure and implemented architecture.

## Sequence

1. identify the diagrams touched by the change
2. list the concrete files, services, routes, workers, queues, or docs the diagrams claim exist
3. compare each claim against the current implementation and committed repo paths
4. remove speculative nodes, edges, or labels that are no longer justified
5. update the diagram to match the implemented architecture only
6. run doc freshness validation and manually review for semantic drift

## Checklist

- every referenced repo path still exists
- every named subsystem is implemented or explicitly committed
- the arrows describe real flow, not wishful future flow
- the text near the diagram still matches the updated shape
- no stale component names survive from an older design

## Stop Condition

If the architecture is still changing too quickly to diagram honestly, delete or defer the diagram instead of forcing a misleading refresh.

## Related Doctrine

- `context/doctrine/mermaid-diagram-freshness.md`
- `context/workflows/perform-doc-freshness-pass.md`
