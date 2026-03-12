# Extend CLI

Purpose: add or change a CLI command cleanly.

Sequence:

1. inspect command registration pattern
2. add input validation and clear output shape
3. keep side effects out of parsing code
4. add success and failure smoke paths

Pitfalls:

- hidden global state
- inconsistent output formatting
