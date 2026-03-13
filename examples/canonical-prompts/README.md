# Canonical Prompt Examples

Use this category for preferred prompt-file and prompt-sequence patterns in prompt-first repos.

Primary files in this category:

- `prompt-first-layout-example.md`
- `001-bootstrap-repo.txt`
- `002-refine-test-surface.txt`

## Verification Metadata

- `prompt-first-layout-example.md`
  Verification level: syntax-checked
  Harness: none
  Last verified by: verification/unit/test_prompt_rules.py
- `001-bootstrap-repo.txt`
  Verification level: syntax-checked
  Harness: none
  Last verified by: verification/unit/test_prompt_rules.py
- `002-refine-test-surface.txt`
  Verification level: syntax-checked
  Harness: none
  Last verified by: verification/unit/test_prompt_rules.py

## A Strong Canonical Prompt Example Should Show

- strictly monotonic numbering
- exact filename references
- one dominant goal per prompt
- staged work that matches actual repo state
- clear mapping from prompt steps to commit-sized outputs

## Choosing This Example

Choose this category when a task should be split into explicit prompts or when a descendant repo stores prompt files as first-class artifacts.

## Drift To Avoid

- renumbered historical prompts
- vague change requests with no file references
- prompts that assume files exist before they are created
