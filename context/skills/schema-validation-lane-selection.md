# Schema Validation Lane Selection

Use this skill to route schema-validation work to the correct lane before
choosing a library or example.

## Procedure

1. Identify the primary goal from task signals.
   - "validate data", "check constraints", "boundary validation" -> Lane A:
     Runtime validation
   - "generate JSON Schema", "export schema", "OpenAPI from models",
     "contract-first", "interoperability artifact" -> Lane B: Contract
     generation
   - "define my type once and get validation + schema", "unified model" ->
     Lane C: Hybrid type-driven
   - "compare libraries", "which validator should I use" -> compare within the
     relevant lane for the target language

2. Confirm the language, then load the relevant stack file:
   `context/stacks/schema-validation-{language}.yaml`

3. Identify the library from the stack's lane fields.
   - Lane A -> `runtime_validation.primary`
   - Lane A named alternate -> `runtime_validation.secondary`
   - Lane B -> `contract_generation.primary`
   - Lane C -> `hybrid_type_driven.primary`
   - If the stack says `not applicable`, state that clearly instead of forcing a
     hybrid answer

4. For Rust, always treat `serde + schemars` as Lane B.
   Runtime validation belongs to `validator` or `garde`. `schemars` exports a
   contract aligned with the `serde` representation; it does not enforce
   runtime acceptance rules.

5. For TypeScript, always distinguish `io-ts` from Zod.
   - Zod: mainstream ergonomic hybrid surface, usually Lane A plus Lane C
   - io-ts: codec-based runtime decode and encode flow with static inference
   - TypeBox + Ajv: contract-first JSON Schema native Lane B path

6. For Python, distinguish Pydantic from `marshmallow`.
   - Pydantic: hybrid type-driven lane with runtime validation and schema export
   - marshmallow: explicit schema object and serialization-first path

7. For Kotlin, compare `Konform` with Hibernate Validator explicitly.
   Do not flatten Kotlin guidance into "annotation-based JVM validation" when
   the operator is asking about Kotlin-first validation design.

8. For Ruby and Elixir, expect Lane C to be unavailable.
   Route to Lane A or Lane B and explain why the ecosystem favors explicit
   runtime validation or separate contract tooling over unified type-driven
   definitions.

9. Load `examples/canonical-schema-validation/CATALOG.md` when it exists to
   confirm which examples exist for the identified lane and language before
   recommending one. During PROMPT_113 foundation work, note that the catalog is
   scheduled for PROMPT_114 and later.

## Priority

Exact lane + exact language (primary library first) > exact lane + adjacent
library with explicit caveat > adjacent lane with the lane shift called out.
Never collapse Lane A, Lane B, and Lane C into one generic "schema validation"
answer.

## Good Triggers

- "how do I validate this struct in Rust"
- "generate JSON Schema from my Pydantic model"
- "which TypeScript library should I use for schema validation"
- "explain the difference between Zod and TypeBox"
- "why is serde + schemars not a validator"
- "compare Konform and Hibernate Validator"
- "show me the contract generation path for Go"

## Avoid

- treating `schemars` as a runtime validator
- treating `marshmallow` and Pydantic as equivalent
- omitting `io-ts` from TypeScript comparisons that claim to be comprehensive
- flattening all three lanes into "schema validation tools"
- loading more than one language stack at a time unless the task is explicitly comparative

## Reference Files

- `context/doctrine/schema-validation-contracts.md`
- `context/stacks/schema-validation-{language}.yaml`
- `examples/canonical-schema-validation/CATALOG.md`
- `examples/canonical-schema-validation/PARITY.md`
