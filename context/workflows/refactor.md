# Refactor

Purpose: improve structure without changing intended behavior.

Sequence:

1. define the boundary that must not change
2. keep tests and smokes green while moving code
3. preserve canonical patterns unless replacing them deliberately
4. update examples only if the preferred pattern changes

Pitfalls:

- hidden behavior changes
- creating a new local pattern accidentally
