# System Operating Manual

This manual is the operational bootloader for coding assistants working inside repositories derived from `agent-context-base`. Use it to stabilize behavior before implementation starts.

## SECTION 1 - What This System Is

The agent-context architecture is a deterministic context assembly system for coding work. It exists to turn normal user requests into a small, relevant working set of doctrine, workflows, stacks, archetypes, manifests, and examples.

It solves a common failure pattern in coding assistants: reading too much, mixing incompatible guidance, inventing architecture, and then implementing against a blurred mental model.

The repository uses layered context instead of flat documentation because different kinds of knowledge have different lifetimes and authority:

- doctrine holds durable rules
- workflows hold task procedures
- stacks hold concrete implementation guidance
- archetypes hold repo-shape guidance
- manifests assemble bounded bundles
- examples show preferred finished patterns
- templates provide scaffolding only

The operating goal is always the same: load only the smallest relevant context required to finish the task correctly.

## SECTION 2 - Core Mental Model

Use this model:

`User request -> routers infer intent -> manifests assemble context -> doctrine constrains behavior -> workflows sequence the work -> examples shape implementation -> validation confirms integrity`

Interpret the request first. Do not start by scanning the whole repo. Routers narrow the task, stack, and archetype. Manifests turn that inference into a concrete context bundle. Doctrine defines what must remain true. Workflows tell you how to execute. Canonical examples show the preferred shape of the final result. Validation tools confirm that the change still fits the system.

This is a deterministic narrowing pipeline, not an invitation to browse widely and improvise.

## SECTION 3 - Context Layers Explained

### Doctrine

Doctrine is the stable rule layer. It defines durable constraints such as minimal context loading, canonical example priority, testing expectations, Compose isolation, Dokku deployment posture, prompt numbering, and stop conditions.

Use doctrine before implementation whenever the task affects behavior, testing, deployment, naming, prompts, or context assembly.

Stability: highly stable.

### Workflows

Workflows are task playbooks. They describe when a workflow applies, what sequence to follow, what outputs are expected, and when smoke tests or minimal real-infra integration tests are required.

Use one primary workflow first. Load a second workflow only when the task genuinely crosses workflow boundaries.

Stability: stable, but task-selected.

### Stacks

Stacks describe concrete implementation surfaces for languages, frameworks, storage systems, queues, and search systems.

Use only the stacks on the active change path. Do not load unrelated stack packs because the repo might support them later.

Stability: stable documents, task-specific selection.

### Archetypes

Archetypes describe repo shape: backend API service, CLI tool, data pipeline, local RAG system, prompt-first repo, Dokku-deployable service, and similar topologies.

Use an archetype when project shape matters more than a single framework choice.

Stability: stable documents, task-specific selection.

### Routers

Routers are the inference layer. They map normal language, repo signals, aliases, and change surfaces onto workflows, stacks, archetypes, and manifests.

Use routers early to narrow the task. Their job is selection, not explanation.

Stability: stable.

### Manifests

Manifests are machine-readable context bundles. They bind routing signals to exact required context, optional context, preferred examples, templates, warnings, and operational defaults.

Use manifests when a manifest closely matches the task and repo shape. Prefer manifest-defined bundles over manual file selection when available.

Stability: stable schema, task-specific selection.

### Examples

Examples are canonical finished patterns. They are higher-authority than templates and should shape implementation structure once the task is already narrow.

Use one preferred canonical example when possible. Avoid blending examples unless resolving an explicit conflict.

Stability: stable examples, task-specific selection.

### Templates

Templates are starter scaffolds. They help bootstrap files and layout, but they are not proof that a pattern is canonical or production-worthy.

Use templates only when scaffolding is needed and never let them override doctrine or canonical examples.

Stability: stable, low-authority.

## SECTION 4 - Assistant Operating Procedure

Follow this sequence:

1. Interpret user intent.
   Map the request from ordinary language to the dominant task. Do not require the user to know internal filenames.

2. Infer the archetype.
   Decide what kind of repo shape the task is operating on. Use one primary archetype unless the repo is intentionally composite.

3. Infer the stack.
   Use touched files, repo signals, lockfiles, frameworks, storage choices, and user language to identify the active stack.

4. Consult the router system.
   Use the task router, stack router, archetype router, alias catalog, and repo-signal hints to narrow the choice set.

5. Load the smallest relevant context bundle.
   Prefer a matching manifest. If no manifest fits cleanly, load the smallest manual bundle in the standard order.

6. Read doctrine constraints.
   Load only the doctrine files relevant to the task before implementation. This prevents policy drift and architecture invention.

7. Consult workflows.
   Load the primary workflow and a second workflow only if the task clearly requires it.

8. Consult canonical examples.
   Prefer one example that matches the active workflow, stack, and archetype. Use preferred examples from the manifest when available.

9. Implement the solution.
   Follow doctrine, workflow sequence, stack guidance, and canonical structure. Keep the solution small and direct.

10. Verify against doctrine and workflows.
   Check that the implementation still matches context-loading rules, testing doctrine, deployment rules, prompt conventions, and stop conditions.

11. Suggest or add smoke tests and minimal real-infra integration tests when appropriate.
   Smoke tests should prove boot and a representative happy path. Significant database-backed or service-boundary changes should also get minimal real-infra integration tests against the isolated test stack.

## SECTION 5 - Context Loading Rules

Use these loading rules:

- load doctrine before implementation when the task affects behavior, testing, deployment, naming, prompts, or example choice
- do not load entire directories unless the task explicitly requires broad maintenance
- prefer manifest-defined bundles over ad hoc bundle assembly
- prioritize canonical examples over templates
- avoid unrelated stacks, archetypes, or examples
- load one primary workflow first
- load one preferred example first
- use anchors only as compact reminders, not as substitutes for doctrine

Expand context only when:

- the task crosses a real storage or service boundary
- stack-specific structure is blocking implementation
- deployment behavior matters
- examples are missing or conflicting
- repo signals disagree with your current inference

Do not load more context to compensate for uncertainty. If ambiguity persists, stop on the missing decision instead of reading widely.

## SECTION 6 - Using Manifests

Manifests define context bundles. They are the system’s assembly instructions.

Read these fields as operational signals:

- `required_context`: files that should be loaded for the profile to be used correctly
- `optional_context`: files that may be loaded if the task expands into adjacent surfaces
- `preferred_examples`: canonical examples that should shape implementation first
- `triggers`: plain-language request patterns that suggest the manifest may fit
- `repo_signals`: file or repo indicators that support or weaken manifest selection

Related fields matter too:

- `archetype`, `primary_stack`, and `secondary_stacks` describe the implementation shape
- `warnings` call out boundary risks and verification expectations
- `recommended_templates` are scaffolds, not authoritative patterns
- `task_hints` help connect the manifest to workflow selection
- `bootstrap_defaults`, Compose names, port bands, and data isolation fields define operational defaults

Use manifests to guide behavior, not just reading order. A good manifest tells you what to load, what to prefer, what to avoid, and how to keep the repo operationally consistent.

## SECTION 7 - Using Canonical Examples

Canonical examples exist to reduce ambiguity at implementation time.

Use them this way:

- let examples guide file shape, handler structure, test structure, deployment wiring, prompt sequencing, or storage integration patterns
- prefer manifest-selected or catalog-ranked examples over ad hoc example choice
- choose one preferred example that matches the active stack and archetype
- avoid blending incompatible examples from different stacks or pattern families

Examples influence code generation by showing the preferred finished surface. They are the model for shape and boundaries. Templates are only starting points.

If no canonical example fits, say so internally, then build the smallest doctrine-consistent solution instead of inventing a broad new pattern family.

## SECTION 8 - Avoiding Failure Modes

Common assistant failures in this architecture:

- loading excessive context before the task is narrow
- inventing architecture not supported by doctrine, routers, or manifests
- introducing frameworks outside the active stack pack
- mixing canonical examples and templates as if they have equal authority
- ignoring doctrine while implementing quickly
- overengineering a simple task into a new subsystem
- reusing default ports or shared Compose names
- mixing primary or dev data with test fixture data

The architecture prevents these failures by separating authority clearly:

- routers narrow the problem early
- manifests define bounded bundles
- doctrine names hard constraints
- example ranking reduces improvisation
- stop conditions block blended guesses
- validation tools catch drift in manifests, examples, prompts, and bootstrap isolation

When in doubt, reduce scope. This system prefers a small correct implementation over a broad speculative design.

## SECTION 9 - Validation And Integrity Tools

Operational tools exist to verify that context and implementation still match the architecture.

- Manifest validation: use `scripts/validate_manifests.py` to check manifest schema, references, naming alignment, and support flags.
- Context linting: use `scripts/validate_context.py` when manifests, routers, examples, templates, prompt numbering, or bootstrap behavior change. This is the broad integrity pass.
- Context bundle preview: use `scripts/preview_context_bundle.py <manifest>` to inspect ordered load sets, ranked examples, anchors, weights, templates, and repo-signal comparisons.
- Prompt analyzer: use `scripts/prompt_first_repo_analyzer.py <repo>` when stack, archetype, workflow, or manifest selection is unclear from repo signals.
- Pattern diff analyzer: use `scripts/pattern_diff.py <left> <right>` to compare an implementation surface against a canonical example or template and spot structural drift.

Use these tools when making architecture-adjacent changes, when routing confidence is low, or when verifying that a repo still fits its claimed profile.

## SECTION 10 - Deployment Awareness

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

Deployment considerations should influence design whenever the task changes service boundaries, storage dependencies, release behavior, migrations, boot flow, environment configuration, or smoke-test expectations.

## SECTION 11 - Working With Prompt-First Repositories

Prompt-first repos have extra determinism requirements.

Follow these rules:

- prompt files use strictly monotonic numbering
- never renumber historical prompts
- never reuse skipped numbers
- prompt references should use explicit filenames and paths
- each prompt should have one dominant goal
- prompt sequences should reflect actual repo state, not assumed future state
- prompt sequences should remain deterministic and easy to continue later

When editing prompt-first repos, protect routing clarity, filename explicitness, and boundaries between doctrine, workflows, examples, and templates.

## SECTION 12 - When To Stop

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

Do not expand scope because more architecture could be added. Return results when the requested change is complete and consistent.

## SECTION 13 - Quick Reference Checklist

- Interpret the task.
- Infer the primary workflow.
- Infer the archetype.
- Infer the stack.
- Consult routers and repo signals.
- Load the smallest relevant bundle.
- Read the needed doctrine.
- Read the primary workflow.
- Load one preferred canonical example.
- Implement the smallest correct solution.
- Verify against doctrine, workflow, deployment, and testing rules.
- Add or recommend smoke tests and minimal real-infra integration tests when the boundary warrants them.
- Stop when the task is complete and context no longer needs to expand.

## SECTION 14 - Final Operational Summary

Think of this architecture as a deterministic context operating system.

Your job is not to browse widely or invent structure. Your job is to route correctly, load the smallest relevant context, obey doctrine, follow the active workflow, use the preferred canonical example, implement the smallest correct change, verify the real boundary, and stop when the work is complete.

The core philosophy is simple:

- smallest relevant context
- deterministic routing
- doctrine-driven behavior
- example-guided implementation
