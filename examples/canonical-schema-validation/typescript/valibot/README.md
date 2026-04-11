# TypeScript - Valibot (Lane A: Modular Runtime Validation)

## Lane
Valibot sits in Lane A with hybrid characteristics. It gives runtime
validation and type inference, but it is optimized around modular imports and
small bundles rather than the broader schema-export story.

## Key Differences from Zod
- Valibot composes validators with `pipe()` instead of method chaining.
- Validators are tree-shakeable, so unused checks are easier to drop from bundles.
- The API surface is smaller and more explicit about each validation step.
- The ecosystem is lighter than Zod's middleware-heavy tooling.
- Type inference is still strong, but the teaching surface is narrower.

## When to Choose Valibot over Zod
Choose Valibot when bundle size matters, especially in edge or mobile-adjacent
environments. It also fits when you want validation steps composed explicitly
instead of hidden inside a longer method chain.
