# TypeScript - io-ts (Lane A: Codec-Based FP Approach)

## Lane
Lane A here means runtime decoding with an explicit error type. io-ts is not a
lighter Zod and it should not be described as one.

## The Codec Model
An io-ts codec is a runtime value that encodes structure plus decode and
encode behavior. `decode()` returns `Either<Errors, T>` instead of throwing,
so invalid input is handled through `Left` and valid input through `Right`.
That makes the failure mode part of the type-level contract. The caller
pattern-matches instead of relying on try/catch.

## When to Choose io-ts
Choose io-ts in FP-heavy TypeScript codebases that already use `fp-ts`, or
when explicit error typing is part of the architectural boundary. It also fits
when codec composition matters more than authoring ergonomics.

## What io-ts is NOT
io-ts is not a simpler Zod. It is a different philosophy centered on codecs,
explicit decode results, and composable functional validation.
