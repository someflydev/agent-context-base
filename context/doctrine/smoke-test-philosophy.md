# Smoke Test Philosophy

Smoke tests prove the simplest meaningful behavior still works.

## What Smoke Tests Should Prove

Smoke tests usually cover:

- process boots
- health or readiness endpoints respond
- one primary user or operator flow succeeds
- critical wiring has not obviously broken

They should run quickly and fail loudly.

## What Smoke Tests Should Not Pretend To Prove

Smoke tests are not a substitute for:

- broad functional coverage
- persistence correctness
- queue semantics
- search correctness
- migration safety

If a feature crosses those boundaries, pair smoke tests with minimal real-infra integration tests.

## Good Smoke Test Traits

- small number of assertions
- deterministic setup
- clear failure messages
- easy to run in CI and locally

## Common Smoke-Test Shapes

- API service: boot, health, one representative route
- CLI tool: command runs, output shape is sane, basic error path
- data pipeline: one small input, one transformed output, one write path
- local RAG system: ingest a tiny corpus and answer one retrieval question

