# System Operating Manual

This manual is the operational bootloader for coding assistants working inside repositories derived from `agent-context-base`. Use it to stabilize behavior before implementation starts.

## SECTION 1 - What This System Is

The agent-context architecture is a deterministic context assembly system for coding work. It exists to turn normal user requests into a small, relevant working set of doctrine, workflows, stacks, archetypes, manifests, examples, and runtime continuity artifacts.

It solves common assistant failure patterns:

- reading too much
- mixing incompatible guidance
- inventing architecture
- forgetting live task state after interruptions
- reloading large areas of the repo to recover what was already known

The repository uses layered context because different kinds of knowledge have different lifetimes and authority:

- doctrine holds durable rules
- workflows hold task procedures
- stacks hold concrete implementation guidance
- archetypes hold repo-shape guidance
- manifests assemble bounded bundles
- examples show preferred finished patterns
- templates provide scaffolding only
- memory preserves current operational state
- handoff snapshots preserve durable transition checkpoints

The operating goal is always the same: load only the smallest relevant context required to finish the task correctly, and preserve continuity at meaningful stop points.

## SECTION 2 - Core Mental Model

Use this model:

`User request -> routers infer intent -> manifests assemble context -> doctrine constrains behavior -> workflows sequence the work -> examples shape implementation -> memory preserves current state -> validation confirms integrity`

Interpret the request first. Do not start by scanning the whole repo. Routers narrow the task, stack, and archetype. Manifests turn that inference into a concrete context bundle. Doctrine defines what must remain true. Workflows tell you how to execute. Canonical examples show the preferred shape of the final result. Memory keeps the current task state recoverable across pauses. Validation tools confirm that the change still fits the system.

This is a deterministic narrowing pipeline, not an invitation to browse widely and improvise.

## SECTION 3 - Context Layers Explained

### Doctrine

Doctrine is the stable rule layer. It defines durable constraints such as minimal context loading, canonical example priority, testing expectations, Compose isolation, Dokku deployment posture, prompt numbering, and stop conditions.

### Workflows

Workflows are task playbooks. They describe when a workflow applies, what sequence to follow, what outputs are expected, and when smoke tests or minimal real-infra integration tests are required.

### Stacks

Stacks describe concrete implementation surfaces for languages, frameworks, storage systems, queues, and search systems.

### Archetypes

Archetypes describe repo shape: backend API service, CLI tool, data pipeline, local RAG system, prompt-first repo, Dokku-deployable service, and similar topologies.

### Routers

Routers are the inference layer. They map normal language, repo signals, aliases, and change surfaces onto workflows, stacks, archetypes, and manifests.

### Manifests

Manifests are machine-readable context bundles. They bind routing signals to exact required context, optional context, preferred examples, templates, warnings, and operational defaults.

### Examples

Examples are canonical finished patterns. They are higher-authority than templates and should shape implementation structure once the task is already narrow.

### Templates

Templates are starter scaffolds. They help bootstrap files and layout, but they are not proof that a pattern is canonical or production-worthy.

### Memory

`MEMORY.md` is the mutable runtime working-state artifact for the current task. It captures the current objective, working set, decisions, findings, scope boundaries, blockers, next steps, and stop condition.

Use it to reduce reload cost across sessions.

Do not use it to replace doctrine, manifests, code inspection, or verification.

### Handoff Snapshots

Handoff snapshots are durable point-in-time transfer artifacts. They preserve meaningful checkpoints for later sessions, later prompts, humans, or other assistants without forcing `MEMORY.md` to become an archive.

## SECTION 4 - Authority Boundaries

Use these distinctions consistently:

- doctrine = stable rules
- manifests = structured context selection
- examples = preferred implementation patterns
- memory = current operational state
- handoff snapshot = durable point-in-time transition artifact

Precedence:

1. code and tests define implementation reality
2. doctrine defines policy and operating constraints
3. manifests define the context assembly contract
4. canonical examples define preferred shape
5. memory and handoff snapshots preserve current state and transfer state

## SECTION 5 - Assistant Operating Procedure

Follow this sequence:

1. Interpret user intent.
2. Infer the archetype.
3. Infer the stack.
4. Consult the router system.
5. Check runtime continuity artifacts.
   Read `MEMORY.md` early if it exists, after stable startup files and basic repo-signal checks.
   Read the latest relevant handoff snapshot only when the task is clearly a resumed transfer.
6. Load the smallest relevant context bundle.
7. Read doctrine constraints.
8. Consult workflows.
9. Consult canonical examples.
10. Implement the solution.
11. Verify against doctrine and workflows.
12. Perform a stop-hook update at meaningful pause points.

## SECTION 6 - Stop Hooks And Continuity

A stop hook is the small continuity update performed before pausing after meaningful work.

At a meaningful stop point:

- refresh `MEMORY.md`
- prune stale sections instead of appending history
- create a handoff snapshot when the pause is likely to cross sessions, prompts, assistants, or humans

Good stop hooks preserve:

- current objective
- active working set
- already inspected files
- decisions already made
- explicitly not doing
- blockers or risks
- next concrete steps
- validation status

Weak stop hooks create transcripts.

## SECTION 7 - Context Loading Rules

Use these loading rules:

- load doctrine before implementation when the task affects behavior, testing, deployment, naming, prompts, or example choice
- do not load entire directories unless the task explicitly requires broad maintenance
- prefer manifest-defined bundles over ad hoc bundle assembly
- prioritize canonical examples over templates
- avoid unrelated stacks, archetypes, or examples
- load one primary workflow first
- load one preferred example first
- use anchors only as compact reminders, not as substitutes for doctrine
- use memory to reduce reload cost, not to widen the bundle

Expand context only when:

- the task crosses a real storage or service boundary
- stack-specific structure is blocking implementation
- deployment behavior matters
- examples are missing or conflicting
- repo signals disagree with your current inference

Do not load more context to compensate for uncertainty. If ambiguity persists, stop on the missing decision instead of reading widely.

## SECTION 8 - Using Manifests

Manifests define context bundles. They are the system’s assembly instructions.

Read these fields as operational signals:

- `required_context`: files that should be loaded for the profile to be used correctly
- `optional_context`: files that may be loaded if the task expands into adjacent surfaces
- `preferred_examples`: canonical examples that should shape implementation first
- `triggers`: plain-language request patterns that suggest the manifest may fit
- `repo_signals`: file or repo indicators that support or weaken manifest selection

Use manifests to guide behavior, not just reading order. A good manifest tells you what to load, what to prefer, what to avoid, and how to keep the repo operationally consistent.

## SECTION 9 - Using Canonical Examples

Canonical examples exist to reduce ambiguity at implementation time.

Use them this way:

- let examples guide file shape, handler structure, test structure, deployment wiring, prompt sequencing, or storage integration patterns
- prefer manifest-selected or catalog-ranked examples over ad hoc example choice
- choose one preferred example that matches the active stack and archetype
- avoid blending incompatible examples from different stacks or pattern families

If no canonical example fits, say so internally, then build the smallest doctrine-consistent solution instead of inventing a broad new pattern family.

## SECTION 10 - Using Memory Without Letting It Drift

Keep `MEMORY.md` small and high-signal.

Recommended habits:

- keep it focused on the current task or prompt batch
- use exact file paths
- rewrite stale sections instead of endlessly appending
- capture active working set whenever practical
- capture `Explicitly Not Doing` when scope control matters
- remove resolved blockers and irrelevant files

`MEMORY.md` can act as a compressed checkpoint inside the context complexity budget because it reduces unnecessary rescanning.

It must not be used to:

- bypass doctrine
- skip manifest or router logic
- skip code verification
- justify loading unrelated context

## SECTION 11 - Derived Repo Guidance

Derived repos do not need heavy process by default.

Practical guidance:

- create a repo-root `MEMORY.md` when work is likely to span sessions
- initialize it at the start of a non-trivial task or at the first meaningful pause point
- use `artifacts/handoffs/` for durable transfer artifacts when needed
- use `handoffs/` only when the lighter convention fits the repo better
- keep small repos lightweight; not every tiny task needs a handoff snapshot

More disciplined usage is appropriate when:

- the repo is prompt-first
- the work spans many prompt runs
- deployment or smoke-test checkpoints matter
- multiple humans or assistants collaborate

## SECTION 12 - Working With Prompt-First Repositories

Prompt-first repos have extra determinism requirements.

Follow these rules:

- prompt files use strictly monotonic numbering
- never renumber historical prompts
- never reuse skipped numbers
- prompt references should use explicit filenames and paths
- each prompt should have one dominant goal
- prompt sequences should reflect actual repo state, not assumed future state
- prompt sequences should remain deterministic and easy to continue later

For prompt-first continuity, `MEMORY.md` should also record:

- highest completed prompt filename
- next intended prompt filename
- prompt numbering decisions already made
- prompt files intentionally deferred or not created

Use exact filenames such as `.prompts/004-refine-memory-scripts.txt`, not vague labels.

Handoff snapshots are especially useful when one prompt run ends and a fresh session will continue later.

## SECTION 13 - Validation And Integrity Tools

Operational tools exist to verify that context and implementation still match the architecture.

- Manifest validation: `scripts/validate_manifests.py`
- Context linting: `scripts/validate_context.py`
- Context bundle preview: `scripts/preview_context_bundle.py <manifest>`
- Prompt analyzer: `scripts/prompt_first_repo_analyzer.py <repo>`
- Pattern diff analyzer: `scripts/pattern_diff.py <left> <right>`
- Memory initialization: `scripts/init_memory.py`
- Handoff creation: `scripts/create_handoff_snapshot.py`
- Memory freshness check: `scripts/check_memory_freshness.py`

Use these tools when making architecture-adjacent changes, when routing confidence is low, when resuming long work, or when verifying that a repo still fits its claimed profile.

## SECTION 14 - Deployment Awareness

This system assumes many descendant projects are simple deployable services with Dokku-oriented deployment.

Design accordingly:

- keep services independently deployable
- keep boot paths explicit
- prefer environment-driven configuration
- keep deployment config close to the service
- keep smoke tests small and able to prove deployed boot behavior

Local Docker-backed environments must follow these rules:

- use `docker-compose.yml` for primary or dev infrastructure
- use `docker-compose.test.yml` for isolated test infrastructure
- set repo-derived Compose `name:` values
- use non-default explicit host ports
- keep dev and test host ports distinct
- keep primary or dev data paths separate from test fixture data paths
- support minimal real-infra integration tests against the isolated test stack for significant database-backed or service-boundary features

## SECTION 15 - When To Stop

Stop expanding scope when these conditions are true:

- the task is completed
- the implementation matches a canonical pattern or the smallest doctrine-consistent pattern
- required tests, smoke tests, or minimal real-infra integration tests were added or recommended where appropriate
- no additional context is required to make the change correctly

Also stop when a doctrine stop condition triggers:

- more than one primary archetype still fits
- more than one stack is plausible for the touched surface
- a storage, queue, search, or deployment change has no minimal verification path
- Compose naming, host-port allocation, or dev-vs-test isolation is ambiguous
- prompt numbering or explicit file references would become non-monotonic or unclear

At a meaningful pause before stopping, perform the stop hook.

## SECTION 16 - Quick Reference Checklist

- Interpret the task.
- Infer the primary workflow.
- Infer the archetype.
- Infer the stack.
- Consult routers and repo signals.
- Read `MEMORY.md` early if it exists.
- Read a handoff snapshot only when a real transfer is being resumed.
- Load the smallest relevant bundle.
- Read the needed doctrine.
- Read the primary workflow.
- Load one preferred canonical example.
- Implement the smallest correct solution.
- Verify against doctrine, workflow, deployment, testing, and prompt rules.
- Update `MEMORY.md` at the next meaningful stop point.
- Create a handoff snapshot when meaningful progress must survive a fresh session or assistant handoff.
- Stop when the task is complete and context no longer needs to expand.

## SECTION 17 - Final Operational Summary

Think of this architecture as a deterministic context operating system.

Your job is not to browse widely or invent structure. Your job is to route correctly, load the smallest relevant context, obey doctrine, follow the active workflow, use the preferred canonical example, keep current task state recoverable through `MEMORY.md`, write handoff snapshots when the checkpoint matters, implement the smallest correct change, verify the real boundary, and stop when the work is complete.

The core philosophy is simple:

- smallest relevant context
- deterministic routing
- doctrine-driven behavior
- example-guided implementation
- practical continuity across sessions
