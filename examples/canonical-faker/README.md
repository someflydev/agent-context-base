# Canonical Faker Examples

## Purpose
These examples exist to demonstrate how to implement realistic synthetic data generation pipelines across multiple languages. They all implement the fictional TenantCore multi-tenant SaaS domain, which introduces realistic complexities like foreign-key dependencies, timestamp causality, non-uniform distributions, and stable ID pools. The arc teaches how to build an explicit relational graph layer on top of standard faker libraries.

## Quick Navigation
- `CATALOG.md` — all examples by language
- `domain/schema.md` — TenantCore entity graph
- `domain/generation-order.md` — canonical 7-stage generation sequence
- `domain/profiles.md` — output profiles (smoke/small/medium/large)
- `domain/validate_output.py` — language-agnostic validator

## The Core Insight
Faker libraries generate realistic atomic values. They do not generate relational systems. The arc explicitly teaches building the graph layer on top: parent-first ordering, ID pools, weighted distributions, temporal realism, and cross-field consistency. Every example demonstrates this pattern.

## Language Examples

| Language     | Primary Library       | Secondary              | Path | Quick Start |
|--------------|-----------------------|------------------------|------|-------------|
| Python       | Faker + Mimesis       | factory_boy            | `python/` | `cd python/faker_pipeline && pipenv run python generators.py` |
| JavaScript   | @faker-js/faker       | Chance                 | `javascript/` | `cd javascript && npm run generate` |
| Go           | gofakeit              | go-faker/faker         | `go/` | `cd go && go run cmd/generate/main.go` |
| Rust         | fake (fake-rs)        | —                      | `rust/` | `cd rust && cargo run --release` |
| Java         | Datafaker             | —                      | `java/` | `cd java && mvn exec:java` |
| Kotlin       | kotlin-faker          | Datafaker              | `kotlin/` | `cd kotlin && gradle run` |
| Scala        | Datafaker (JVM)       | —                      | `scala/` | `cd scala && sbt run` |
| Ruby         | faker                 | ffaker                 | `ruby/` | `cd ruby && bundle exec ruby generate.rb` |
| PHP          | FakerPHP/Faker        | Nelmio Alice           | `php/` | `cd php && php generate.php` |
| Elixir       | Faker                 | ExMachina              | `elixir/` | `cd elixir && mix run -e "TenantCore.Generator.run()"` |

## Validation
All examples produce JSONL output that can be validated:
```bash
python3 domain/validate_output.py --input-dir {language}/output/smoke
```