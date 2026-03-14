# Perform Doc Freshness Pass

Use this workflow after major implementation milestones or whenever repo docs may have drifted.

## Goal

Make docs, READMEs, and diagrams match the implementation closely enough that they remain trustworthy inputs for humans and assistants.

## Sequence

1. identify the files changed in the implementation pass
2. list the docs, READMEs, diagrams, and prompts that mention those surfaces
3. update or remove statements that are now inaccurate, speculative, or stale
4. refresh Mermaid diagrams only if the architecture is implemented enough to describe honestly
5. run the doc-governance validation checks
6. do one manual pass for semantic freshness that automation cannot prove

## Minimum Checks

- cross-links still resolve
- startup instructions reference real files and commands
- README claims match implemented scope
- diagrams do not mention removed or renamed paths
- example and template guidance still matches the repo’s current doctrine

## Output

- docs updated in the same change set as the implementation, or
- explicit defer notes where front-facing docs still should not exist

## Related Commands

```bash
python scripts/validate_doc_governance.py
python scripts/validate_context.py
```

## Related Doctrine

- `context/doctrine/documentation-timing-discipline.md`
- `context/doctrine/mermaid-diagram-freshness.md`
