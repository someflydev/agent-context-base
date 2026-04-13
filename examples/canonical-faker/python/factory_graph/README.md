# factory_boy Graph

This directory shows `factory_boy` as a declarative object-graph layer for
TenantCore. The focus is readability for smoke or small datasets, not raw
throughput.

Use `factory_boy` when:

- you want to describe object construction with `SubFactory`, `Trait`,
  `Sequence`, and lazy attributes
- you are building smoke fixtures or small example datasets

Use the raw Faker or Mimesis pipelines when:

- you need medium or large profile throughput
- you want direct dict generation without Python object-factory overhead

This graph is not intended for large profiles.
