# Add Scraping Source

## Purpose

Add a scrape-based source adapter without turning the repo into an unbounded crawler.

## When To Use It

- no usable API exists for required data
- the scrape target is permitted and operationally feasible

## Inputs

- target pages or listing flow
- robots and terms review
- selectors or extraction rules
- retention location for fetched HTML or files

## Sequence

1. confirm scraping is justified versus API or export options
2. document robots, terms, pacing rules, and anti-bot constraints
3. fetch the smallest stable unit: page, detail document, or file
4. archive raw HTML or files before parsing
5. isolate selectors and extraction logic in the parser stage, not transport code
6. add change-detection notes for selectors, pagination, and document layout
7. verify one representative scrape path against archived fixtures or captured raw pages

## Outputs

- scrape adapter
- raw document capture
- selector-aware parser contract

## Related Doctrine

- `context/doctrine/source-research-discipline.md`
- `context/doctrine/raw-data-retention.md`
- `context/doctrine/sync-safety-rate-limits.md`

## Common Pitfalls

- treating a browser automation step as the default when plain HTTP is enough
- hard-coding brittle selectors in orchestration code
- scraping aggressively without per-source pacing

## Stop Conditions

- robots or terms posture is incompatible
- selectors are too unstable to justify the source
- the scraper cannot explain how it resumes after partial pagination failure
