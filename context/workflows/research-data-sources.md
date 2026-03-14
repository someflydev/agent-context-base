# Research Data Sources

## Purpose

Evaluate candidate public or partner data sources before writing adapters.

## When To Use It

- a repo needs a new upstream source
- the team is deciding between API access and scraping
- licensing, reliability, or freshness is unclear

## Inputs

- target domain or record type
- required fields and freshness expectations
- expected sync cadence

## Sequence

1. define the minimum fields, identifiers, and freshness the product needs
2. identify candidate APIs, feeds, exports, or scrape targets
3. compare terms, rate limits, robots posture, auth, and historical access
4. assess whether the source supports incremental syncs or only full pulls
5. capture reliability risks: schema churn, anti-bot controls, unstable pagination, missing IDs
6. choose a primary source, fallback source, and ingest method

## Outputs

- source shortlist
- recommended ingest path
- known legal and operational constraints

## Related Doctrine

- `context/doctrine/source-research-discipline.md`
- `context/doctrine/data-acquisition-philosophy.md`

## Common Pitfalls

- picking the easiest source before checking licensing or freshness
- assuming a scrape target is stable because one page worked once
- ignoring the fallback source until after the primary breaks

## Stop Conditions

- the chosen source lacks required identifiers or fields
- licensing or robots posture is incompatible with the repo goal
- no repeatable incremental sync strategy is available and a full reload is operationally unacceptable
