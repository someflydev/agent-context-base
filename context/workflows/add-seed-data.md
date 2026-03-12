# Add Seed Data

Use this workflow when a repo needs repeatable starter data for dev or test use.

## Preconditions

- the target data store is known
- the seed audience is known: dev, test, or both

## Sequence

1. define what the seed data exists to prove or enable
2. separate dev seed paths from test fixture paths
3. add deterministic, minimal records
4. wire invocation paths clearly
5. test the seed flow against isolated infrastructure
6. make sure reset operations cannot hit dev data when intended for test data

## Outputs

- seed files or scripts
- documented seed commands
- validation of the seed path

## Related Docs

- `context/doctrine/compose-port-and-data-isolation.md`
- `examples/canonical-seed-data/README.md`

## Common Pitfalls

- sharing mutable seed data between dev and test
- seeding far more data than the workflow needs
- leaving destructive reset targets ambiguous

