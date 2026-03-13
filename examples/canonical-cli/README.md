# Canonical CLI Examples

Use this category for preferred command, flag, and output-structure patterns.

Primary file in this category:

- `python-cli-command-example.py`

## Verification Metadata

- `python-cli-command-example.py`
  Verification level: behavior-verified
  Harness: none
  Last verified by: verification/examples/python/test_cli_examples.py

## A Strong Canonical CLI Example Should Show

- clear command hierarchy
- explicit flags and defaults
- readable structured output
- smoke-test pattern for the main invocation
- integration-test pattern when a command touches real storage or services

## Choosing This Example

Choose this category when adding commands, subcommands, or operator-facing workflows.

## Drift To Avoid

- clever but obscure command naming
- hidden side effects
- no distinction between human-readable output and machine-usable output
