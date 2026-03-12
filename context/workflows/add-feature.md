# Add Feature

Purpose: add a new capability without losing local conventions.

Sequence:

1. confirm archetype and active stack
2. load relevant doctrine
3. inspect canonical example for the nearest pattern
4. implement the smallest coherent vertical slice
5. add smoke coverage and integration coverage if boundaries are touched
6. update docs only where durable behavior changed

Pitfalls:

- broad refactors disguised as feature work
- skipping example lookup
