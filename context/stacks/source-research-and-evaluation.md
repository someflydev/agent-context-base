# Source Research And Evaluation

Use this pack when the work starts before implementation and the main question is which upstream source should exist in the repo at all.

## Typical Repo Surface

- research notes or source scorecards
- licensing and robots review
- field coverage comparison
- freshness and historical access notes
- recommended ingest strategy and fallback source

## Decision Surfaces To Watch

- legal or terms posture
- stable identifiers
- incremental sync support
- reliability and schema churn
- anti-bot or auth burden

## Expected Outputs

- chosen primary source
- rejected alternatives with reasons
- recommended adapter type: API, feed, file, or scrape

## Common Assistant Mistakes

- choosing the most convenient source without checking terms
- ignoring fallback sources
- starting implementation before confirming identifiers and freshness requirements
