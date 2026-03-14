# Add Classification Step

## Purpose

Add post-parse categorization, tagging, or enrichment with explicit provenance.

## When To Use It

- normalized records need categories, quality scores, or downstream routing labels
- a rule-based or model-based enrichment stage is being introduced

## Inputs

- normalized record contract
- classification policy or rubric
- confidence or provenance requirements

## Sequence

1. define what the classifier decides and what evidence it can use
2. keep classification after normalization unless source-local quirks make that impossible
3. write classifier outputs with version, rationale, and confidence when feasible
4. preserve pre-classification normalized data unchanged
5. add one regression example for a borderline record

## Outputs

- classifier or enricher stage
- explicit classification metadata
- test examples for stable categories

## Related Doctrine

- `context/doctrine/data-acquisition-philosophy.md`

## Common Pitfalls

- hiding category rules inside parsing code
- overwriting source facts with inferred labels
- omitting classifier version or evidence

## Stop Conditions

- classification changes cannot be traced to a rule or model version
- downstream storage no longer distinguishes source facts from derived labels
- the stage cannot be replayed from normalized inputs
