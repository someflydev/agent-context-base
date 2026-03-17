# Manifest Selection

Use this skill to choose between near-match manifests without merging or guessing.

## Procedure

1. list the candidate manifests that match the task and repo signals
2. read `context/router/repo-signal-hints.json` if it exists — it is machine-readable authority and supersedes manual comparison
3. score each manifest by signal strength:
   - **strong**: lockfile match, framework entrypoint, migration directory, Compose file
   - **weak**: one-off comment, doc-only mention, speculative reference
4. prefer the manifest backed by two or more strong signals over one backed by a single weak signal
5. when signal strength is equal, prefer the manifest with the narrower scope (fewer optional context items) — narrower scope reflects a more precise task match
6. if no manifest is clearly dominant after scoring, stop: state the ambiguity explicitly and do not proceed

## Good Triggers

- "two manifests look equally relevant"
- "which manifest should I use"
- "manifest tie-breaking"
- "how to pick between manifests"
- "I see multiple manifests that might apply"

## Avoid

- choosing a manifest based on one transient file alone
- merging two near-match manifests into a combined bundle
- picking the manifest that loads the most context as a hedge against uncertainty
- proceeding when the dominant manifest is still unclear — raise the ambiguity instead
