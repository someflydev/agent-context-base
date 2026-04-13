# Canonical Faker Rust Example

This example shows two distinct Rust surfaces:

- `fake-rs` derive support on a non-relational `AddressSnapshot`
- a `PipelineBuilder` that keeps the TenantCore relational graph explicit

Rust makes the pool pattern hard to ignore. The generator cannot pretend that
memberships, projects, and audit events appear from atomic faker calls alone;
it has to carry typed vectors and maps forward stage by stage.

## What It Demonstrates

- deterministic seeding through `StdRng::seed_from_u64`
- parent-first generation order from organizations through audit events
- explicit `org_member_map` ownership instead of hidden mutable globals
- validation before output

## Quick Start

```bash
cargo run -- --profile smoke --output ./output --format jsonl
```

## Test

```bash
cargo test
```

## Validate Output

```bash
python3 ../domain/validate_output.py --input-dir ./output/smoke
```

This example stays intentionally small: no database, no async runtime, and no
framework wiring. The teaching surface is the generation pipeline itself.
