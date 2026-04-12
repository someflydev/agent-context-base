# TypeScript - Zod (Lane C: Hybrid Type-Driven)

## Lane
Lane C means one Zod schema yields three behaviors. `z.infer<>` gives the
static TypeScript type, `.parse()` or `.safeParse()` gives runtime validation,
and `zod-to-json-schema` exports the contract artifact.

## Key Patterns Used
- `discriminatedUnion()` for tagged payload and source config variants.
- `superRefine()` for plan limits, timestamp ordering, and duplicate checks.
- `z.infer<>` for static types derived from the runtime schema.
- `schema_export.ts` for JSON Schema export plus an Ajv drift check.
- Explicit `nullable()` fields where the fixture corpus distinguishes null from absence.

## Comparison with io-ts
Zod is the ergonomic mainstream option: method chaining, direct `.parse()`,
and a relatively small cognitive surface. io-ts is built around codec values
that explicitly model decode and encode behavior as runtime objects. That makes
io-ts more FP-oriented and more explicit at the boundary where decoding can fail.

## Comparison with Valibot
Valibot keeps the same general validation-plus-inference story but pushes much
harder on modular imports and bundle-size trimming. Zod has a larger ecosystem
and is the more common teaching default.

## Running
```bash
npm run validate
node --import tsx src/schema_export.ts
```
