# Polyglot Validation Lab

Use this archetype for cross-language validation and contract experiments where
the main goal is comparison, teaching, or parity, not a deployable service.

## Shape

A set of canonical examples organized by language and validation lane
(`A` / `B` / `C`), sharing one problem domain and one fixture corpus. This is a
reference implementation area for comparison and instruction, not production
middleware.

## When to Use This Archetype

- building cross-language schema validation comparison examples
- teaching runtime validation versus contract generation distinctions
- evaluating library ergonomics across Pydantic, Zod, serde + schemars, and peers
- showing the same domain problem solved in multiple languages or library styles

## Required Doctrine

- `context/doctrine/schema-validation-contracts.md`
- `context/doctrine/testing-philosophy.md`

## Required Patterns

- organize examples by language and lane
- keep one shared domain model and one shared fixture corpus
- state whether the example targets runtime validation, contract generation, or hybrid flow
- make schema drift checks explicit when an exported artifact is part of the example

## Routing

When the task is primarily about cross-language validation comparison, schema
export teaching, or library philosophy tradeoffs, prefer this archetype over
`polyglot-lab`. Route here before a service archetype when the repo surface is
meant to teach or compare rather than ship an application.

## Canonical Examples

- `(canonical examples will be in examples/canonical-schema-validation/ — created in PROMPT_114)`

## Not Suitable For

- production validation middleware in an application service
- single-language validation tooling with no comparison goal
- api contract management systems that center on service delivery

## Key Doctrine

- `context/doctrine/schema-validation-contracts.md`
