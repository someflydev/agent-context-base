# Validation Modules

These files are the canonical validation narratives used to compose `.acb/specs/VALIDATION.md`.

They are intentionally separate from `context/specs/` because validation is not decorative prose. It is the main autonomy rail for generated repos.

The repo-local `.acb/validation/` directory then adds two generated artifacts:

- `CHECKLIST.md` for session-useful proof obligations
- `MATRIX.json` for future machine reasoning about coverage, drift, and orchestration
