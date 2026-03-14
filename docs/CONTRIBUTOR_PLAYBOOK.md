# Contributor Playbook

This playbook explains how to extend `agent-context-base` without weakening the routing model, the context system, or the verification posture that makes the repository reliable for both humans and assistants.

## 1. Purpose of the Contributor Playbook

Large AI-assisted systems degrade quickly when contributors add new capabilities without shared extension rules. A repo like this does not only store code. It stores routing logic, context packs, canonical examples, manifests, templates, and verification assets that assistants actively use to make implementation decisions.

Without strict extension discipline, the common failure modes are predictable:

- stack definitions drift across `context/stacks/`, `manifests/`, `examples/catalog.json`, and `verification/`
- examples look canonical but are not actually verified
- near-duplicate patterns compete for authority and make routing ambiguous
- documentation grows faster than the architecture and starts contradicting code or manifests

This playbook protects system integrity by requiring contributors to extend the repo as a set of aligned artifacts, not as isolated files. The rule is simple: if a new capability changes what assistants may build, route, or trust, then the related context, examples, manifests, and verification metadata must evolve together.

## 2. Architectural Principles Contributors Must Respect

Every extension must preserve the repository's existing operating model.

### Context discipline

Assistants should route first and load later. New artifacts must help the system choose a smaller context bundle, not justify loading more files by default. Keep guidance narrow and scoped to one problem class.

### Verification-first engineering

A new pattern is not first-class because it is well described. It becomes trustworthy when it has a clear verification level, registry metadata, and the right harness or structural checks. Prefer extending `verification/` early rather than treating it as follow-up work.

### Canonical examples as architectural anchors

Canonical examples in `examples/` are preferred implementation patterns, not illustrative filler. Add them only when the pattern is stable enough to teach. One strong example is better than several overlapping examples with unclear ranking.

### Bounded assistant autonomy

The architecture assumes assistants should move quickly only when the workflow, stack, archetype, example, and verification path are clear. New capabilities must preserve that clarity. If an extension creates ambiguity, the extension is incomplete.

### Incremental system evolution

Promote new capabilities in small slices. Add one stack, one archetype, or one example family at a time, then prove it. Avoid broad speculative expansions that introduce multiple unverified boundaries at once.

### Clear artifact authority

Keep boundaries intact:

- `context/doctrine/` for stable rules
- `context/workflows/` for task sequences
- `context/stacks/` for framework and infra specifics
- `context/archetypes/` for repo shape
- `manifests/` for the smallest justified bundle
- `examples/` for canonical patterns
- `templates/` for scaffolding only
- `verification/` for trust

Do not collapse these responsibilities into one oversized document.

## 3. Adding New Stacks

Adding a stack means teaching the system a new implementation grammar. That requires more than a new markdown file.

### Required stack surfaces

A new stack usually touches:

- `context/stacks/<stack-name>.md`
- one or more `manifests/*.yaml`
- `examples/catalog.json`
- `verification/example_registry.yaml`
- `verification/stack_support_matrix.yaml`
- `examples/` and `verification/examples/` if new canonical examples are introduced
- `verification/scenarios/` when runtime verification is needed

If the stack materially changes routing, also review `context/router/`.

### Use the stack expansion system, not ad hoc docs

In this repo, stack expansion is the coordinated process of:

1. defining the stack pack in `context/stacks/`
2. binding it into one or more manifests
3. attaching canonical examples in `examples/`
4. ranking those examples in `examples/catalog.json`
5. declaring trust and harness coverage in `verification/example_registry.yaml`
6. recording maturity and known gaps in `verification/stack_support_matrix.yaml`

If any of those layers are missing, the stack is only partially integrated.

### What to define for each stack

Every stack addition should make the following explicit:

- stack name: stable, concise, and consistent across filenames and metadata
- language: the implementation language or languages
- framework: the primary application framework
- primary libraries: the opinionated supporting libraries that shape code structure
- archetype compatibility: which repo shapes the stack supports
- example types: which example families the stack needs to be useful

For backend stacks, example types should usually include:

- API endpoint example
- HTML fragment example
- data endpoint example
- runnable minimal app when the stack is a first-class runtime target

### Role of `PROMPT_11_t.txt` and stack expansion prompts

Prompt-first expansion work should be treated as an implementation aid, not a replacement for manifests or verification. The repo's prompt validation logic in `verification/unit/test_prompt_rules.py` supports filenames like `PROMPT_11_t.txt`, where:

- `11` is the prompt step number
- `_t` marks a template companion for that numbered step

That means stack expansion can be staged through prompt sequences while preserving monotonic numbering and explicit references. Use stack expansion prompts when the work needs to be split into auditable steps such as:

- add the stack pack
- add or refine manifests
- add canonical examples
- add verification harnesses
- refine docs after the new capability is proven

When using prompt files, keep them monotonic, give each file one dominant goal, and reference exact repository paths. Do not let prompt files become the source of truth for the stack. The durable sources remain the stack pack, manifests, examples, and verification metadata.

### Canonical example expectations for new backend stacks

Backend stacks should demonstrate the three recurring surfaces already used across `examples/canonical-api/`:

- API endpoints: request decoding, response shape, and route registration
- HTML fragment responses: partial-render or server-rendered fragment patterns for interactive UI updates
- data endpoints: structured payloads for charts, tables, or reporting surfaces

These examples should feel like small real systems, not toy syntax fragments.

### Docker-backed verification

Docker-backed verification is recommended for backend stacks because it proves buildability and a minimal request path without forcing every contributor to install each language toolchain locally. If a backend stack is meant to become first-class, provide a runnable runtime bundle and a scenario in `verification/scenarios/` that can verify container build, boot, and a minimal probe path.

## 4. Designing Canonical Examples

Canonical examples should be minimal, clear, and representative of real work. They are not marketing samples. They are implementation anchors that assistants may copy from directly.

### Core rules

- keep the example as small as possible while still showing the preferred pattern
- show one dominant pattern per file
- include real naming and plausible data flow
- avoid speculative abstractions that the stack pack does not endorse
- prefer examples that match one stack and one archetype cleanly

### API example guidelines

API examples should show:

- route declaration
- parameter decoding or validation
- separation between transport and business logic
- response serialization
- representative error handling

### HTML fragment example guidelines

HTML fragment examples should show:

- the server-side render path
- the fragment boundary, not a full-page application
- the data shape needed to render the fragment
- naming that makes partial-update usage obvious

### Data endpoint example guidelines

Data endpoint examples should show:

- a stable JSON shape for reporting or chart consumers
- deterministic ordering where relevant
- light transformation logic that reflects real usage
- a clear boundary between fetch, transform, and response assembly

### Runtime bundle examples

If the stack supports runnable runtime bundles, add a minimal app that composes the key example surfaces into one small, verifiable shape. These runtime bundles are the preferred place to prove Docker-backed smoke coverage.

### Example README expectations

Each example family README should document:

- primary files in the category
- verification level
- harness name or `none`
- where verification last runs from
- what a strong example in that category should show

This pattern already exists in files such as `examples/canonical-api/README.md` and `examples/canonical-prompts/README.md`. Follow it rather than inventing a new README style.

## 5. Expanding the Verification System

Verification keeps the repo honest. Whenever contributors add a new stack, example, or runtime pattern, they should decide how the system will prove that addition stays trustworthy.

### Main verification components

- `verification/example_registry.yaml`
  The authoritative registry of canonical examples, verification levels, targets, harnesses, and confidence.
- `verification/stack_support_matrix.yaml`
  The explicit maturity view for each supported stack.
- `verification/examples/`
  Stack-specific tests and structure checks.
- `verification/scenarios/`
  Runtime or harness helpers for runnable examples.
- `scripts/verify_examples.py`
  Targeted example verification entrypoint.
- `scripts/run_verification.py`
  Tiered verification runner.
- `scripts/validate_context.py`
  Repo integrity and context consistency checks.

### How to extend verification

When adding a new stack or example:

1. add or update the example registry entries
2. assign an honest verification level
3. record the stack's verified coverage and missing coverage
4. add stack-specific tests in `verification/examples/`
5. add a scenario harness when runtime proof is needed
6. make README metadata agree with registry metadata

### Choosing the right verification level

Use the maturity ladder in `verification/policies/canonical-example-levels.md`.

- `draft` only when the repo must track work that is not yet trustworthy
- `syntax-checked` for parseable or structurally validated examples
- `smoke-verified` when the example or runtime bundle boots and answers a minimal path
- `behavior-verified` when one real behavior is asserted beyond boot
- `golden` only for strong, stable examples that should outrank peers during selection

Do not claim a higher level than the harness proves.

### Verification commands contributors should run

At minimum, contributors extending the base should run:

```bash
python3 scripts/validate_context.py
python3 scripts/run_verification.py --tier fast
python3 scripts/verify_examples.py --stack <stack-name>
```

If the extension adds or changes a runtime bundle, contributors should also run the relevant medium or heavy checks that exercise Docker or native runtime paths.

## 6. Designing New Archetypes

Archetypes represent repo shape. They tell assistants what kind of system they are building before the assistant reasons about stack details.

Existing examples include:

- backend API services
- data pipelines
- CLI tools
- local RAG systems
- prompt-first repos
- automation or deployment-oriented service shapes

### Why archetypes matter

Archetypes reduce ambiguity about:

- expected directory structure
- likely workflows
- appropriate canonical examples
- default verification posture
- common supporting stacks

### When a new archetype is appropriate

Add a new archetype only when the repo shape is materially different from existing archetypes. A new framework alone is not a new archetype. Good reasons include:

- the system class has a different runtime boundary
- the work centers on a different primary asset, such as prompts, pipelines, indexes, or CLIs
- the verification posture differs in a durable way
- assistants need different workflow and example selection rules

### Archetype design guidelines

New archetypes should:

- describe the repo shape, not a specific implementation language
- point to the minimum relevant workflows and doctrine
- name the common stacks that fit
- explain what assistants should optimize for in that repo class
- avoid duplicating stack-specific rules

Keep new archetype files in `context/archetypes/` concise. If the file starts teaching framework APIs, that content belongs in a stack pack or canonical example instead.

## 7. Expanding the Context System

The context system is the knowledge base assistants rely on during routing and implementation. It is intentionally split into narrow artifact types so assistants can load only what the task justifies.

### Main context artifact types

- doctrines in `context/doctrine/`
- stack packs in `context/stacks/`
- archetype packs in `context/archetypes/`
- workflow guides in `context/workflows/`
- small reminder anchors in `context/anchors/`

### Rules for adding context artifacts

- add a new artifact only when the guidance is durable and likely to recur
- prefer extending an existing focused file over creating a near-duplicate
- keep each file scoped to one authority boundary
- link to existing docs instead of restating them
- write for fast scanning by assistants under context limits

### Avoiding redundancy

Before adding a new context file, check whether the information already belongs in:

- an existing doctrine
- a stack pack
- an archetype
- a workflow
- a canonical example

If the proposed content repeats those files with slightly different wording, it should not be added.

### High-density writing

Context artifacts should be short, directive, and operational. Use them to reduce decision cost. Avoid long narrative explanations unless the concept is impossible to state concisely.

## 8. Documentation Discipline

Documentation should evolve with the system, but it should not become a competing architecture layer.

### Documentation rules

- update docs when the mental model changes, not for every minor refactor
- link to the authoritative file instead of copying its content
- prefer one durable explanation over several similar ones
- keep repo-wide docs aligned with manifests, examples, and verification
- remove or rewrite stale claims quickly when the architecture changes

### What to avoid

- duplicate explanations across `docs/`, `context/`, and `examples/`
- overly verbose prose that hides the operational rule
- conflicting descriptions of stack support or verification posture
- README files that claim a stronger trust level than the registry or tests support

This repository is optimized for information density. Documentation should clarify routing and extension, not create more text for assistants to sift through.

## 9. Maintaining Assistant Compatibility

Extensions must remain compatible with real assistant runtimes, which means contributors need to think about how a model will discover, rank, and use the new capability under limited context and imperfect recall.

### Compatibility constraints

- context size: keep files small enough to load selectively
- information density: prefer direct rules, examples, and metadata over prose padding
- predictable directory structure: put new artifacts in the established layer
- clear naming: stack, example, and archetype names should remain stable across files
- explicit trust: assistants need verification level and harness visibility to rank examples correctly

### Design implications

Contributors should preserve:

- one clear place to find stack-specific guidance
- one clear manifest story for bundle selection
- one or a small number of canonical examples per pattern family
- one explicit verification path for each promoted capability

If assistants would need to infer too much from scattered docs, the extension is not ready.

## 10. Extension Checklists

Use these checklists before opening a PR or treating a capability as first-class.

### Checklist: adding a new stack

1. Add `context/stacks/<stack-name>.md`.
2. Update or add manifests that bind the stack into the correct bundle.
3. Define stack name, language, framework, primary libraries, archetype compatibility, and example expectations.
4. Add or update canonical examples and rank them in `examples/catalog.json`.
5. Add entries to `verification/example_registry.yaml`.
6. Update `verification/stack_support_matrix.yaml`.
7. Add or extend stack-specific tests and scenario harnesses as needed.
8. Run `python3 scripts/validate_context.py`.
9. Run targeted verification with `python3 scripts/verify_examples.py --stack <stack-name>`.

### Checklist: adding canonical examples

1. Confirm the pattern is stable enough to teach.
2. Add the example under the correct `examples/canonical-*` family.
3. Keep the example minimal and representative.
4. Update the family README with files, verification level, and harness details.
5. Add the example to `examples/catalog.json`.
6. Add registry metadata in `verification/example_registry.yaml`.
7. Add or extend tests that justify the chosen verification level.
8. Re-run targeted verification for that example or stack.

### Checklist: expanding verification harnesses

1. Decide whether the change needs structural, smoke, behavior, or runtime proof.
2. Add or update tests in `verification/examples/`.
3. Add or update a scenario in `verification/scenarios/` when runtime probing is needed.
4. Keep the harness small and deterministic.
5. Update registry and support-matrix metadata to match the new trust level.
6. Run the relevant tier locally.

### Checklist: introducing a new archetype

1. Confirm an existing archetype cannot describe the repo shape cleanly.
2. Add `context/archetypes/<archetype-name>.md`.
3. Link the minimum doctrine, workflow, and stack surfaces needed.
4. Add or refine manifests that select the new archetype.
5. Add canonical examples only when the shape has a stable preferred pattern.
6. Update routing hints if the new archetype changes discovery.
7. Validate manifests and context integrity.

### Checklist: expanding the context system

1. Check whether an existing doctrine, workflow, stack pack, or archetype already owns the content.
2. Add the new artifact only if it introduces genuinely new reusable guidance.
3. Keep the file narrow and directive.
4. Add links rather than duplicate prose.
5. Verify that manifests and examples still point to the correct artifacts.

## 11. Example Extension Scenarios

These scenarios show how to apply the rules in practice.

### Scenario: adding a new backend language stack

Suppose contributors want to add a new backend stack for a language that is not yet first-class. The safe path is:

1. create a stack pack in `context/stacks/`
2. wire that stack into a backend archetype manifest
3. add canonical API, HTML fragment, and data endpoint examples
4. add a runnable minimal app if the stack is intended to be first-class
5. register the examples, assign honest verification levels, and add a scenario harness
6. record missing coverage in `verification/stack_support_matrix.yaml`

The mistake to avoid is stopping after step 1 or step 3. A stack without manifests and verification is not actually integrated.

### Scenario: expanding canonical examples for an existing stack

Suppose an existing backend stack has a JSON route example but lacks a stronger HTML fragment example. Contributors should:

1. add the new fragment example in the existing canonical family
2. update the family README
3. add the example to the catalog and registry
4. extend the existing stack test file in `verification/examples/`
5. raise the stack support entry only if the new coverage is truly verified

This is an example extension, not a new stack or archetype. Keep the change scoped accordingly.

### Scenario: introducing a new archetype for a different project class

Suppose contributors want to support a durable new class of system such as an automation-heavy repo with a different repo shape from backend services and pipelines. Contributors should:

1. prove that current archetypes cannot describe the shape cleanly
2. create a new archetype file focused on repo structure and workflow expectations
3. add or refine manifests that bind the right doctrine, workflows, and stack packs
4. add canonical examples only for recurring patterns unique to that archetype
5. update verification only where the new repo shape changes trust requirements

The main guardrail is not to disguise a stack preference as an archetype.

### Scenario: using prompt-sequence expansion for staged capability work

Suppose a stack expansion is large enough that contributors want staged prompt artifacts. A sequence can reserve a numbered slot with a template prompt such as `PROMPT_11_t.txt`, then use later prompts to land manifests, examples, and verification in reviewable slices. That is acceptable only if the durable artifacts remain the real source of truth and the prompt sequence follows monotonic numbering and exact path references validated by `verification/unit/test_prompt_rules.py`.

## Closing Rule

Extend the system the same way the system already operates: route narrowly, add one coherent capability at a time, prove it with verification, and keep context, examples, manifests, and documentation aligned. If a change would make assistants guess more, the change is not complete yet.
