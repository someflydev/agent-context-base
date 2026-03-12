# Fix Bug

Purpose: correct behavior with the smallest safe change.

Sequence:

1. identify failing path
2. reproduce with test or smoke path
3. inspect the canonical local pattern
4. patch the root cause
5. add or tighten regression coverage

Pitfalls:

- fixing symptoms only
- skipping verification
