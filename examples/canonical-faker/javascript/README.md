# JavaScript / TypeScript TenantCore Example

This example demonstrates a deterministic TenantCore generator in TypeScript
using `@faker-js/faker` for atomic field generation and Chance for weighted
sampling, non-uniform counts, and edge-case injection.

Key teaching points:
- Seed both `faker` and Chance with the same seed before any generation call.
- Use distribution helpers for plan, region, and skewed per-org counts instead
  of relying on uniform randomness.
- Keep relational graph integrity in the pipeline layer; faker only supplies
  field values.

Quick start:

```bash
npm install
npm run generate -- smoke
```

Run tests:

```bash
npm test
```

Validate generated output:

```bash
python3 ../domain/validate_output.py --input-dir ./output/smoke
```

Generation order follows the shared six-stage TenantCore sequence:
organizations, users, memberships, projects, api keys, invitations, and audit
events.
