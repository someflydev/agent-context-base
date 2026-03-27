## CLI Architecture

Keep argument parsing, command execution, and side-effecting integrations separate. Commands should be thin wrappers around explicit operations so validation can prove behavior without scraping terminal state by hand.

Prefer small command modules and deterministic output formatting over monolithic shell-like entrypoints.
