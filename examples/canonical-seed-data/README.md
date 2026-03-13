# Canonical Seed Data Examples

Use this category for preferred dev seed and test fixture patterns.

Primary file in this category:

- `polars-seed-data-example.py`

## Verification Metadata

- `polars-seed-data-example.py`
  Verification level: behavior-verified
  Harness: polars_data_pipeline
  Last verified by: verification/examples/python/test_polars_examples.py

## A Strong Canonical Seed Example Should Show

- clear distinction between dev seed data and test fixture data
- deterministic records
- explicit reset boundaries
- invocation path for seeding
- small integration test proving the seed path works

## Choosing This Example

Choose this category when adding starter data, fixture loading, or reset workflows.

## Drift To Avoid

- shared mutable seed data between dev and test
- oversized seed sets
- destructive reset commands with unclear targets
