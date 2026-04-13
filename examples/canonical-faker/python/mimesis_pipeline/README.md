# Mimesis Pipeline

This pipeline demonstrates Mimesis as a schema-first atomic value generator for
TenantCore. Organizations are seeded with `Schema` and `Field`, and the rest of
the graph is built explicitly on top of those values.

Performance note: Mimesis is usually faster than Faker at large volumes because
`Schema.create(iterations=N)` batches atomic generation more efficiently than a
pure Python loop.

Prefer Mimesis when:

- you want a schema-as-code style for roots or flat entities
- you care about faster large-profile generation
- you still intend to keep referential integrity in explicit graph code

Prefer Faker when:

- you need broader locale coverage and ecosystem familiarity
- you want custom providers with the common faker API surface
