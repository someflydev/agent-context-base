# Faker Pipeline

This pipeline demonstrates three Faker-specific techniques on top of the shared
TenantCore graph layer:

- mixed-locale generation with `Faker(['en_US', 'en_GB', 'de_DE', 'fr_FR'], use_weighting=True)`
- a custom provider for weighted TenantCore `plan` and `region` enums
- 5% edge-case users with near-limit emails, non-ASCII names, and `UTC`

Typical generation time:

- `smoke`: under 1 second once dependencies are installed
- `small`: a few seconds on a laptop
- `medium`: tens of seconds and best used for local demos

The relational graph and cross-field rules still come from the shared
`../domain/generation_patterns.py` module. Faker supplies realistic atomic
values; it does not enforce org membership, project ownership, or event timing.
