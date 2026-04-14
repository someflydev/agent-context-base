# Canonical Faker Example: Elixir

This example demonstrates generating synthetic datasets using Elixir.

## Features
- **Atoms**: Uses `Faker` for atomic field generation.
- **Contrast**: `ExMachina` is included for contrast. Note that ExMachina is good for simple test fixtures, but **not** for relational graph generation, as it does not enforce cross-field temporal or state constraints.
- **Delivery**: Exposes a Mix task `mix generate`.
- **Determinism**: Uses `:rand.seed/2` for process-level seeding.
- **Pipeline**: Uses a functional pipeline idiom with `Enum.map` over entity ranges. For medium/large profiles, replace Enum with Stream.

## Quick Start
```bash
mix deps.get
mix generate --profile smoke
```

## Testing
```bash
mix test
```
