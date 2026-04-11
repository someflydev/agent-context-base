# WorkspaceSyncContext Domain

`WorkspaceSyncContext` is the shared problem space for the schema-validation
arc. It was chosen because it exercises nested models, discriminated unions,
cross-field rules, enum handling, nullable versus optional behavior, and
contract export pressure without depending on one language’s framework style.

Every language example in this arc implements the same five models, consumes
the same JSON fixtures, and documents any allowed divergence in `PARITY.md`.
That keeps the comparison focused on validation and contract-generation
philosophy instead of on different product domains.
