# Context Engineering Guide

Context engineering is the practice of designing the information environment within which assistants reason and act.

In `agent-context-base`, context is not treated as a pile of prompt text or a transcript to be accumulated indefinitely. It is treated as an engineered operating surface with structure, authority boundaries, loading rules, compression rules, and continuity mechanisms. The quality of that surface strongly determines whether an assistant can produce coherent code, preserve architectural intent, verify the right boundary, and continue work across long-running sessions.

This guide explains how assistants should think about context as an engineering discipline rather than as passive input. Its purpose is to make context selection and maintenance deliberate, bounded, and explainable.

## Section 1 - Why Context Engineering Matters

Assistant performance depends less on total available information than on the quality of the active information environment.

Poor context produces predictable failures:

- context overload, where too many files compete for attention and no pattern remains dominant
- missing architectural signals, where key repo-shape or stack cues were never loaded
- conflicting information, where doctrine, examples, and local code point in different directions
- irrelevant examples, where adjacent but unrelated patterns distort implementation choices
- low information density, where long text adds little decision value but still consumes working capacity

These failures are structural. They do not come primarily from a lack of raw intelligence. They come from forcing the assistant to reason inside a noisy, weakly curated environment.

Context engineering improves reasoning reliability by changing the environment itself:

- it preserves dominant architectural signals
- it keeps active knowledge bounded to the current task
- it raises the relative weight of high-authority artifacts
- it reduces opportunities for cross-stack contamination
- it makes escalation and expansion explicit instead of accidental

In practice, effective context engineering determines whether assistants:

- produce coherent architectures instead of blended hybrids
- maintain long-term reasoning across multiple work phases
- avoid hallucinated patterns that are unsupported by the repo
- scale to larger systems without scanning them indiscriminately

The central claim is simple: context quality is not a convenience concern. It is a primary determinant of correctness.

## Section 2 - Context As An Information Architecture

Context should be treated as an engineered structure rather than an unstructured conversation history.

Conversation history is only one possible input surface, and it is a poor default architecture for serious development work. Histories grow opportunistically, mix durable and temporary information, flatten authority, and make it difficult to distinguish policy from observation or current state from stale state.

This repository instead organizes context through explicit artifact classes:

- doctrine for durable rules and operational constraints
- stack packs for concrete framework and infrastructure guidance
- archetype packs for repo-shape and system-form guidance
- canonical examples for preferred verified patterns
- workflow guides for task sequencing and proof expectations
- routers and manifests for selecting bounded context bundles
- memory artifacts for preserving current operational state

These artifacts exist because different kinds of knowledge have different jobs:

- doctrine should survive across tasks
- stack knowledge should activate only on the relevant implementation surface
- archetype knowledge should shape project form only when repo shape matters
- canonical examples should constrain implementation style once the route is narrow
- workflows should sequence action and verification
- memory should preserve continuity without becoming a second source of truth

This separation makes context legible and governable. Instead of asking, "What should I read next?" the assistant can ask higher-quality questions:

- What kind of knowledge is missing?
- What authority level does it need?
- Is the task blocked by policy, shape, pattern, or current state?
- What is the smallest artifact that resolves that uncertainty?

That is the transition from prompt handling to context engineering.

## Section 3 - Context Layers

Context is most reliable when organized into layers with distinct lifetimes and authority.

A useful layered model in this architecture is:

1. architectural doctrine
2. stack knowledge
3. archetype knowledge
4. project-specific memory
5. task-specific instructions

Each layer answers a different question.

`architectural doctrine`

- What must remain true?
- What loading, testing, naming, deployment, and stop-condition rules govern the work?

`stack knowledge`

- How does this framework, language, or infra component behave?
- What file surfaces, patterns, and verification implications does it impose?

`archetype knowledge`

- What kind of system is this?
- Does the repo behave like a backend API service, prompt-first repo, CLI, data pipeline, or local RAG system?

`project-specific memory`

- What is happening right now in this repo?
- What decisions, inspected files, blockers, and next steps must survive interruption?

`task-specific instructions`

- What does the user want in this session?
- What boundary is being changed now?

Assistants should load these layers incrementally rather than all at once.

Recommended reasoning order:

1. interpret the task and repo signals
2. load the minimum doctrine required to avoid violating stable rules
3. load the active workflow and stack or archetype material only if the task requires them
4. load memory artifacts for continuity if the task is resumed or long-running
5. load canonical examples only after the route is narrow enough for a dominant pattern to exist

Layering matters because it prevents authority collapse. A memory note should not overrule doctrine. A canonical example should not decide repo shape if the archetype is still unresolved. A long user message should not replace stack guidance. Good layering keeps each artifact in its proper role.

## Section 4 - Context Density

Information density is the amount of useful decision-making signal carried per unit of context.

High-density context carries a large amount of relevant guidance with minimal noise. Low-density context consumes attention without materially improving decisions.

High-density context usually looks like:

- structured documentation with clear scope
- concise examples tied to a known pattern
- explicit architectural descriptions
- machine-readable manifests with concrete triggers and required files
- short continuity artifacts that capture current state precisely

Low-density context usually looks like:

- verbose prose with little operational consequence
- broad code dumps without explanation of why they matter
- transcripts of earlier reasoning that no longer affect decisions
- multiple near-duplicate examples competing for pattern authority
- large unrelated file sets loaded "just in case"

Assistants should prefer density over volume. That means preferring:

- structured documentation over free-form commentary
- one strong canonical example over several weak analogies
- direct architectural descriptions over inferred folklore
- exact file paths and conclusions over long narrative reconstruction

Density is not the same as brevity. A dense artifact can be substantial if nearly every section carries active constraints or implementation value. The real question is whether the loaded material changes the assistant's reasoning in a useful way.

If a file is long but decisive, it may be worth loading. If it is short but irrelevant, it still reduces context quality.

## Section 5 - Context Selection

Context selection is the act of deciding what enters the active working set.

In this architecture, assistants should not begin from the assumption that more context is safer. The safer path is usually to start narrow and expand only when the current bundle cannot justify the next correct decision.

Selection should follow these principles:

- start with minimal context
- load only what is required to explain the current task
- use routers and manifests to locate high-value artifacts
- prefer bounded bundles over ad hoc scanning
- treat every loaded artifact as consuming part of a context complexity budget

The practical selection sequence is:

1. interpret the user request
2. inspect narrow repo signals
3. infer the dominant workflow
4. infer the active stack and archetype only on the touched surface
5. consult routers and aliases
6. select the best-fit manifest
7. load required context first
8. load optional context only if the task clearly activates it

Routers and manifests exist to make selection deterministic.

- routers normalize natural language and repo signals into candidate workflows, stacks, and archetypes
- manifests bind those inferences to machine-readable context bundles

This prevents selection from degenerating into vague browsing.

Context complexity budgeting constrains selection further. Even when many files are potentially relevant, not all of them belong in the first-pass bundle. A budget forces prioritization:

- doctrine before adjacent commentary
- one workflow before several overlapping playbooks
- one dominant example before several plausible examples
- the active stack before neighboring ecosystems

Selection quality can often be judged by a simple test: can the assistant explain why each loaded artifact is necessary for the current task? If not, the bundle is probably too broad.

## Section 6 - Context Expansion

Context expansion is the controlled act of loading more information after the initial bundle has been assembled.

Expansion is appropriate when the current bundle is insufficient to solve the task correctly. It is not appropriate as a reflex whenever uncertainty appears.

Typical valid expansion triggers include:

- the task crosses an additional stack or storage boundary
- the current workflow exposes a new verification surface
- a canonical example is needed to resolve implementation shape
- deployment behavior becomes relevant
- local code inspection reveals a project-specific pattern not covered by the first bundle

Examples of disciplined expansion:

- loading additional stack documentation when a change crosses from an HTTP handler into a database integration
- consulting a canonical smoke-test example when the implementation is complete but proof shape is still unclear
- reviewing architecture docs when the task affects repo shape instead of a single code surface

Expansion should be gradual:

1. identify the exact uncertainty
2. classify what kind of artifact can resolve it
3. load the smallest relevant artifact
4. re-evaluate whether the task is now unblocked
5. stop expanding once the next decision becomes clear

This approach prevents "context creep," where each small uncertainty triggers a wider scan until the assistant is operating inside a noisy, weakly prioritized bundle.

The guiding rule is that context should expand only when necessary to solve the current task, not to create a feeling of completeness.

## Section 7 - Context Compression

Context compression is the process of preserving useful conclusions while removing no-longer-necessary bulk.

Compression becomes necessary when the working set grows beyond what is needed for reliable reasoning or continuity. Without compression, long-running sessions tend to accumulate stale investigation trails, obsolete alternatives, and repeated architectural deductions.

Effective compression strategies include:

- summarization of long explored branches into a few durable conclusions
- memory checkpoints that preserve current state without replaying the full path
- removing obsolete information that no longer governs the next step
- replacing long reasoning trails with concise decisions and supporting evidence

Good compression preserves:

- current objective
- active boundary
- decisions already made
- important rejected options
- verification status
- next concrete steps

Good compression discards:

- repeated exploration
- stale hypotheses
- raw code blocks that are no longer needed as active references
- outdated blockers that have already been resolved

`MEMORY.md` is a primary compression mechanism in this architecture. It supports compression by turning live task state into a small, high-signal checkpoint. It should preserve operational continuity, not historical narration.

Used well, `MEMORY.md` reduces reload cost because the next session can recover:

- what the task is
- what files matter
- what was learned
- what remains

without reloading the entire previous reasoning trace.

Compression is therefore not an afterthought. It is how long-running work remains stable under bounded context.

## Section 8 - Context Evolution Over Time

Context requirements change as a project matures.

Early project stages tend to require broader exploration at the shape level:

- archetype selection
- stack exploration
- workflow choice
- initial doctrine and example alignment

Later project stages usually require deeper project-specific context:

- local architectural conventions
- existing module boundaries
- current verification surfaces
- continuity artifacts such as `MEMORY.md` and handoff snapshots

This means assistants should not hold a static model of what "enough context" looks like. The right context depends on project phase.

In early stages, assistants should emphasize:

- repo-shape clarity
- stack and deployment fit
- canonical pattern selection
- avoiding premature invention

In later stages, assistants should emphasize:

- preserving local architectural intent
- understanding already-established module boundaries
- tracking current task state precisely
- compressing history into durable working memory

The transition between these phases matters. A common failure is to keep reasoning as if the project is still being invented long after it has acquired strong local patterns. Another failure is the reverse: assuming mature local patterns exist before the repo has stabilized its first architecture.

Assistants should continually ask:

- Is the current problem mostly about choosing a shape, or extending an established one?
- Is the highest-value context generic stack knowledge, or repo-specific memory and code structure?
- Has the project crossed from exploration into continuity-heavy maintenance?

Context engineering must adapt to those answers over time.

## Section 9 - Canonical Examples As Context Anchors

Canonical examples are critical because they anchor implementation in verified or intentionally curated patterns.

They provide:

- reliable implementation references
- structural guidance for recurring problem types
- architectural anchors that reduce invention pressure
- a concrete answer to "what should a good version of this look like here?"

Without canonical examples, assistants are more likely to synthesize patterns from weak analogies, generic training priors, or blended repo fragments. That is one of the main routes to hallucinated architecture.

Assistants should consult canonical examples before inventing new patterns, especially when:

- the task matches a known recurring implementation family
- file shape or handler structure is ambiguous
- testing or smoke-test structure needs a reference
- the repo supports several stacks and pattern dominance must be preserved

Examples should be used carefully:

- prefer the example selected by the active manifest or example catalog
- choose one dominant example rather than several near-matches
- use a second example only when it covers an orthogonal concern such as smoke tests
- do not blend incompatible examples across stacks or archetypes

Canonical examples act as context anchors because they stabilize the assistant's internal model. They reduce the need to improvise by making preferred finished shapes visible and concrete.

If no canonical example fits, the assistant should explicitly recognize that absence and produce the smallest doctrine-consistent solution rather than silently inventing a new pattern family.

## Section 10 - Context Failure Modes

Context engineering fails in recurring ways. These failures should be treated as diagnosable system problems, not as random model behavior.

Common failure modes include:

- loading entire repositories unnecessarily
- mixing unrelated stacks into one working set
- overloading context with raw code instead of higher-signal architectural artifacts
- losing architectural intent because current local patterns were never identified
- allowing memory artifacts to override doctrine or code reality
- loading many plausible examples and removing pattern dominance
- expanding context to compensate for ambiguity instead of stopping on the missing decision

These failures have recognizable symptoms.

`loading entire repositories unnecessarily`

- the assistant opens broad directories without a route
- many files are technically related but few are necessary
- implementation quality drops despite increased reading

`mixing unrelated stacks`

- terminology from different ecosystems appears in one solution
- code shape resembles several frameworks at once
- verification strategy becomes incoherent

`overloading context with raw code`

- large code dumps dominate reasoning
- doctrine and examples lose authority
- architecture is inferred from accidental adjacency rather than explicit guidance

`losing architectural intent`

- the change fits generic software patterns but not the repo's real design
- local abstractions are bypassed
- deployment, testing, or continuity expectations drift

Assistants should detect and correct these failures by:

1. identifying the dominant source of noise or contradiction
2. shrinking the active bundle back to the smallest decisive artifacts
3. re-establishing the route through doctrine, workflows, stacks, archetypes, and examples
4. resuming implementation only after pattern dominance is clear again

Correction usually requires subtraction before addition.

## Section 11 - Context Engineering Workflow

Context engineering should be practiced as a repeating workflow during development rather than as a one-time startup step.

A standard loop is:

1. interpret intent
2. select minimal context
3. plan work
4. execute tasks
5. verify results
6. update memory
7. compress context

Each stage has a distinct purpose.

`interpret intent`

- determine the real task boundary
- avoid loading context for adjacent but inactive problems

`select minimal context`

- use routers, manifests, and repo signals
- assemble the smallest bundle that can support the first correct action

`plan work`

- identify the dominant workflow
- define the verification surface before implementation expands

`execute tasks`

- work inside the selected bundle
- expand only when the current boundary justifies it

`verify results`

- test the changed boundary at the right level
- confirm that the implementation matches the selected architectural pattern

`update memory`

- preserve current state for the next pause or session
- record only what materially reduces future reload cost

`compress context`

- prune obsolete detail
- retain conclusions, decisions, and next steps

This workflow repeats throughout long-running sessions. Every substantial change, boundary crossing, or pause point is a chance to re-run the loop at a smaller scale.

The result is not merely better context hygiene. It is a more stable operating model for sustained development.

## Section 12 - Context In Autonomous Sessions

Context discipline becomes more important as assistant autonomy increases.

A highly autonomous assistant can move quickly, but speed amplifies the effects of poor context selection. If the working set is noisy or weakly bounded, autonomy does not create leverage. It creates faster drift.

Autonomous sessions therefore require stronger context discipline:

- respect context complexity budgets
- avoid loading irrelevant knowledge
- preserve architectural clarity before optimizing for momentum
- define stop conditions when route or authority is ambiguous
- compress and update memory at meaningful pause points

Autonomy should operate inside a controlled information environment, not replace one.

In practical terms, this means an autonomous assistant should be able to explain:

- why the current bundle is sufficient
- what would justify loading more
- which artifact currently dominates implementation shape
- what proof will establish correctness
- what state must be preserved before pausing

The more freedom an assistant has to act, the more carefully its context must be engineered.

## Section 13 - Context In Multi-Agent Systems

Multiple assistants often share context indirectly rather than through a shared live conversation.

In this architecture, multi-agent collaboration happens through repository artifacts that preserve decisions, current state, and architectural intent across sessions and actors.

Important shared artifacts include:

- memory files such as `MEMORY.md`
- architecture and doctrine documentation
- handoff snapshots
- manifests and router definitions
- canonical examples and verification-oriented workflow guides

These artifacts enable multi-agent collaboration because they externalize state and structure:

- memory files preserve current operational continuity
- documentation preserves durable architectural rules
- handoff snapshots preserve a durable checkpoint at a transfer boundary
- manifests preserve how bounded context should be assembled
- canonical examples preserve preferred implementation patterns

This matters because agents rarely fail only by forgetting facts. They fail by inheriting a noisy or ambiguous information environment from previous work. Good shared artifacts make the next assistant start from a stable surface instead of reconstructing intent from scattered code and partial history.

Multi-agent context engineering should therefore optimize for:

- explicit authority boundaries
- compact high-signal handoffs
- clear distinction between durable policy and current task state
- enough detail to prevent rework, but not enough to recreate transcripts

The goal is indirect coordination through engineered artifacts rather than accidental continuity through accumulated chat.

## Section 14 - Designing Future Context Systems

Context engineering will continue to evolve from manual discipline toward more automated systems.

Likely future capabilities include:

- automated context routers that infer bundles with higher precision
- dynamic context summarization that compresses long sessions into validated checkpoints
- knowledge graphs that expose architectural relationships between code, doctrine, examples, and workflows
- retrieval-based context loading that is constrained by authority and route rather than by lexical similarity alone
- more explicit scoring systems for context density, ambiguity, and bundle fitness

The current architecture is designed to support those capabilities because it already separates:

- durable rules from mutable state
- routing from loading
- examples from templates
- continuity from doctrine
- bundle selection from implementation

That separation is what makes future automation possible. Systems cannot optimize context well if all knowledge is mixed into one undifferentiated prompt surface.

The long-term direction is not to eliminate human judgment. It is to make context selection, compression, and continuity more systematic, inspectable, and reproducible.

Foundational principle:

Context is not merely what the assistant sees.

Context is the engineered information environment that shapes what the assistant can reliably think, infer, preserve, and build.

Treating context that way is what turns AI-assisted development from prompt improvisation into runtime architecture.
