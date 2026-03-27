---
acb_origin: canonical
acb_source_path: context/specs/product/base.md
acb_role: product
acb_version: 1
---

## Baseline Product Intent

The repo must make its intended product or operator-facing purpose explicit enough that a future assistant can distinguish core behavior from scaffolding. Specs should describe stable outcomes, not implementation trivia.

Every meaningful feature slice should answer:

- who or what consumes the result
- what boundary becomes newly true
- what behavior would count as broken
- which validation result proves the slice is real
