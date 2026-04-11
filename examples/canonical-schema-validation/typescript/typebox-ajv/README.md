# TypeScript - TypeBox + Ajv (Lane B: Contract-First, JSON Schema Native)

## Lane
Lane B means the contract is primary. TypeBox schemas are already JSON Schema,
so the same object can be validated with Ajv and exported directly for other
languages or tools.

## Key Distinction from Zod
Zod derives JSON Schema through a transformation layer. TypeBox schemas already
are JSON Schema, and `Static<>` extracts the TypeScript type from that schema.
That is a schema-first mental model rather than a type-first one.

## Limitations
Cross-field rules such as plan versus `max_sync_runs` need JSON Schema
conditionals or application-level enforcement. Pure schema validation cannot
express every business rule cleanly, so this example documents that boundary.
