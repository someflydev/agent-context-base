# Source Research Discipline

Research candidate sources before implementation so the repo does not optimize around the wrong upstream.

## Evaluation Order

1. confirm the source is legally and operationally usable
2. confirm it exposes the fields, identifiers, and freshness the product actually needs
3. confirm update mechanics: cursor, date filter, sitemap, feed, pagination, export, or none
4. confirm long-term reliability: auth stability, robots posture, schema churn, and historical access

## Minimum Research Record

- source name and owner
- access method: API, feed, file dump, or scraping
- licensing or terms summary
- rate limit or crawl posture
- key fields and stable identifiers
- freshness expectations
- anti-bot or auth constraints
- recommended ingest strategy

## Decision Rule

- prefer official APIs over scraping when the API exposes sufficient coverage and practical limits
- prefer scraping only when needed fields are absent, blocked, or materially delayed elsewhere
- prefer sources with stable identifiers and incremental pull support

## Comparison Rule

Always compare at least two candidate sources when the repo will depend on the data operationally. A single-source assumption made too early usually becomes an architecture defect.

## Output Rule

End research with a recommended source, a fallback option, and one explicit reason the rejected option lost.
