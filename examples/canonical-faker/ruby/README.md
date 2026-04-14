# Ruby Canonical Faker Example

This directory demonstrates synthetic data generation in Ruby using two approaches:
1. `faker` (primary): A full relational pipeline with a complete entity graph.
2. `ffaker` (contrast): A partial implementation demonstrating how to use `ffaker`, which is generally faster and simpler but supports fewer locales.

## Important Note for Rails Teams
Ruby has a strong fixture-generation culture rooted in `FactoryBot` (for Rails).
This example focuses on raw output generation, not ORM fixtures. `FactoryBot` is the idiomatic tool for Rails contexts. This example shows that faker's output becomes a relational dataset only when you build the graph layer explicitly in your own Ruby code, which is useful for non-Rails contexts or decoupled raw dataset generation.

## Two Random Sources
Generation uses two separate random number generators:
- `Faker::Config.random` is set once at startup to ensure reproducible outputs from faker calls.
- `Random.new(seed)` is explicitly passed to distributions and bounded counts to decouple distribution structural choices from simple string generation.

## When to use FFaker vs Faker
- **ffaker** does not support as many locales as faker. For a US-English-only dataset, ffaker is faster.
- **faker** is preferred for multi-locale datasets or when a rich set of generation types is needed.

## Quick Start
```bash
bundle install
ruby generate.rb --profile smoke
```

## How to Test
```bash
bundle exec rspec
```

## How to Validate
```bash
python3 ../../domain/validate_output.py --input-dir ./output/smoke
```