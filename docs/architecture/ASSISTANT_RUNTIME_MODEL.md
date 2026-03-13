# Assistant Runtime Model

`agent-context-base` is best understood as a runtime system for AI-assisted development rather than a static prompt library or a generic starter repository. Its purpose is to transform human intent into verified code through a controlled sequence of interpretation, context selection, implementation, verification, and continuity management. The repository does this by separating concerns into explicit layers, giving both humans and assistants a stable operating model for long-lived software work.

The architecture is deliberately narrow. It does not assume that larger context produces better outcomes. It assumes the opposite: that reliable AI development requires bounded context, explicit routing, canonical implementation references, proof-oriented execution, and memory artifacts that preserve state without replacing source code or doctrine. In that sense, the repository functions like a development runtime with policy, routing, state, and validation surfaces.

## Section 1 - Why AI Systems Need Runtime Architecture

Naive AI coding environments tend to fail for structural reasons rather than purely model-quality reasons. The common failure mode is not that the assistant cannot write code at all. It is that the assistant operates without a stable runtime model, so each session improvises its own startup procedure, context boundary, architectural assumptions, and verification standard.

That failure appears in several recurring forms:

- context explosion, where the assistant reads too much adjacent material and loses the dominant pattern for the task
- loss of architectural coherence, where stacks, examples, or repo shapes are blended into hybrids that were never actually designed
- unverified outputs, where code looks plausible but was never proved against the real runtime boundary it changes
- unbounded autonomy, where momentum replaces decision discipline and the assistant keeps expanding scope to resolve uncertainty
- lack of reproducibility, where two sessions begin from different files, make different inferences, and produce inconsistent results

These are runtime failures, not merely documentation failures. They happen because the system has no enforced path from request to implementation.

`agent-context-base` solves this by introducing explicit runtime layers. Human intent does not go straight to code generation. It passes through planning, routing, knowledge retrieval, bounded execution, verification, and memory persistence. Each layer has a distinct responsibility and an authority boundary:

- doctrine defines what must remain true
- routers define how intent is classified
- manifests define what context is allowed into the active bundle
- canonical examples define what patterns should dominate implementation
- verification defines what proof is sufficient for the changed boundary
- memory defines how operational state survives interruption without becoming a second source of truth

The result is an architecture that treats AI development as an engineered system. The assistant is not expected to “remember everything” or “figure it out from the whole repo.” It is expected to operate inside a runtime that narrows decision space, enforces verification posture, and preserves continuity across sessions.

## Section 2 - Overview of the Runtime Model

The runtime model in this repository can be described as a layered transformation pipeline:

`Human Intent`
`-> Planning`
`-> Context Selection`
`-> Knowledge Retrieval`
`-> Execution`
`-> Verification`
`-> Memory Persistence`

Each stage corresponds to a runtime layer:

- Human Intent Layer
- Assistant Planning Layer
- Context Routing Layer
- Knowledge Layer
- Execution Layer
- Verification Layer
- Memory Layer

The core architectural claim is that high-quality AI development is not one act of generation. It is a sequence of controlled transformations. A human states a goal. The assistant converts that goal into a bounded plan. The runtime selects the minimum relevant context. Structured knowledge constrains the implementation shape. Execution produces artifacts. Verification tests whether those artifacts actually satisfy the intended boundary. Memory preserves the operational state that the next session will need.

This layered sequence is what makes the repository behave like a runtime environment rather than a pile of instructions. The layers are not decorative categories. They form a control flow. Each layer narrows or validates the next one.

## Section 3 - Human Intent Layer

The Human Intent Layer is the entrypoint into the runtime. It is where the human operator defines the development objective and establishes the problem boundary the rest of the system must honor.

In this architecture, intent commonly enters through:

- initial prompts that define the main task
- refinement prompts that sharpen or constrain an in-progress task
- planning prompts that ask the assistant to classify, scope, or sequence work before implementation

This layer is intentionally simple. It does not need to specify internal repository vocabulary. The system is designed to infer the correct workflow, stack, and archetype from normal language plus repository signals. That is why concise prompts, often in the 2 to 5 sentence range, are usually optimal. They communicate the real problem without flooding the assistant with premature structure or forcing early overfitting to implementation details.

Strong intent at this layer usually expresses:

- the problem domain, such as backend API, prompt-first repo, local RAG system, data pipeline, or CLI
- important constraints, such as verification requirements, deployment posture, repository boundaries, or time-boxed scope
- possible stack signals, when the human already knows the likely ecosystem
- deployment goals, when the task must preserve a Dokku surface, Docker-backed isolation, or another operational boundary

The Human Intent Layer influences every downstream layer. It determines what kind of planning is necessary, which router paths are plausible, which manifests are eligible, which examples should rank highest, which verification surfaces matter, and what memory needs to be preserved. If intent is broad but clear, the system can still route safely. If intent is ambiguous at a structurally important boundary, the runtime is designed to stop rather than guess.

This is a major architectural choice. The system treats unclear intent as a reason to narrow or halt, not as permission to load more unrelated context.

## Section 4 - Assistant Planning Layer

The Assistant Planning Layer converts human intent into an executable internal model. Its role is not to write code yet. Its role is to determine what kind of work is being requested and what bounded path through the system should govern that work.

In this repository, planning is responsible for:

- identifying the dominant task archetype
- identifying the likely implementation stack
- scoping the initial project or change architecture
- breaking work into phases or vertical slices
- defining the first verification target before implementation starts
- surfacing stop conditions when the route is not yet stable

This is where the assistant distinguishes, for example, between:

- a backend API change and a prompt-first repo maintenance task
- a storage-backed feature and a documentation-only refinement
- a single-stack change and a multi-boundary operation that requires additional verification discipline

Planning prevents chaotic code generation by forcing a small number of structural decisions up front. Without this layer, the assistant can easily begin implementing the first plausible interpretation, then compensate for later contradictions by expanding context and rewriting architecture midstream. That pattern is one of the main causes of hallucinated system design.

Within `agent-context-base`, planning is tightly connected to the boot sequence and the workflow layer. The assistant is expected to determine one dominant workflow, one primary archetype when project shape matters, and one active stack grammar on the touched surface. It is also expected to work in reviewable vertical slices rather than broad speculative rewrites.

Planning mode workflows matter because they give the assistant a bounded decomposition strategy. Instead of “build the whole thing,” the planning layer typically produces a sequence such as:

1. classify the repo or task
2. identify the first slice
3. define the verification surface
4. implement the slice
5. refine only after proof exists

That sequence is what keeps the runtime conservative without becoming rigid.

## Section 5 - Context Routing Layer

The Context Routing Layer is the core narrowing mechanism of the runtime. It decides which subset of repository context the assistant is allowed to treat as active for the current task.

This layer is implemented through several cooperating artifacts:

- routers, which map natural language and repo signals to workflows, stacks, and archetypes
- manifests, which define bounded context bundles in machine-readable form
- doctrine, which encodes stable rules and operational constraints
- stack packs, which provide concrete ecosystem-specific implementation guidance
- archetype packs, which describe repository shape and system form

The routing system exists because AI assistants degrade when context is uncontrolled. A repository like this one contains many valid patterns across multiple ecosystems, deployment postures, and workflow types. If the assistant reads broadly, it does not become “more informed.” It becomes more likely to mix incompatible patterns.

Routing prevents that by turning free-form discovery into explicit selection.

The process is conceptually:

1. infer the dominant task from the human request
2. inspect narrow repo signals to infer stack and archetype candidates
3. consult router docs and alias mappings to normalize language
4. select the best-fit manifest
5. assemble a minimal ordered context bundle from that manifest

Manifests are especially important because they bind routing decisions to actual file sets. A manifest does not merely say “this looks like a FastAPI task” or “this repo is prompt-first.” It declares required context, optional context, preferred examples, recommended templates, repo signals, warnings, compose defaults, isolation expectations, and other operational metadata that the assistant can use deterministically.

This layer also incorporates context complexity budgeting. The repository explicitly recognizes that bounded context is not a stylistic preference but a runtime constraint. Routers and manifests may propose candidate files, but the budget decides what is reasonable to include in the first-pass bundle. This keeps the assistant from escalating every uncertainty into more reading.

The Context Routing Layer is the primary defense against:

- context explosion
- cross-stack contamination
- blended archetypes
- false thoroughness
- architecture drift caused by excessive example loading

## Section 6 - Knowledge Layer

The Knowledge Layer contains the structured artifacts that shape implementation once routing has narrowed the active context. It is the repository’s curated knowledge substrate.

This layer includes:

- canonical examples
- stack documentation
- workflow doctrine
- architecture and operating notes

Its purpose is not to provide general information. Its purpose is to provide the right information at the right stage of the runtime.

The main knowledge classes have distinct roles:

- doctrine provides durable rules, such as minimal context loading, canonical-example priority, testing expectations, prompt monotonicity, stop conditions, and isolation constraints
- workflows provide task sequences, such as how to add a feature, bootstrap a repo, add smoke tests, refactor safely, or extend a CLI
- stack packs provide implementation grammar for specific ecosystems
- archetype packs describe repo shape and system boundaries
- architecture notes and system docs explain how the runtime itself behaves
- canonical examples provide preferred completed patterns that should dominate generated output

Canonical examples are especially important because they function as verified reference implementations. They are not mere snippets. They are curated patterns with verification metadata, confidence, and in many cases harness-backed checks. Their purpose is to answer the question: “What should this kind of implementation look like in this runtime?”

That makes them architecturally powerful. They reduce the assistant’s freedom to invent structure. The runtime first narrows the active stack and archetype, then ranks examples appropriate to that route, then prefers one dominant example rather than several near-matches. This sequencing is critical. Knowledge retrieval happens after routing so the assistant does not use examples as discovery tools and accidentally blend unrelated shapes.

The Knowledge Layer therefore preserves architectural coherence by giving the assistant bounded, high-authority reference points instead of forcing it to synthesize patterns from memory.

## Section 7 - Execution Layer

The Execution Layer is where the assistant acts inside the current repository or inside a generated descendant repository. Once intent has been planned, context has been routed, and knowledge has been selected, execution produces concrete development artifacts.

Common activities in this layer include:

- writing code
- editing configuration
- creating modules or routes
- generating or updating documentation
- building service scaffolding
- adding smoke or integration tests
- updating manifests, prompts, or memory artifacts when the task requires it

This layer is deliberately incremental. The repository favors reviewable vertical slices over broad speculative rewrites. A vertical slice usually means one bounded path that can be implemented and verified end to end. For example:

- one API route plus one smoke test
- one prompt batch plus manifest updates
- one storage integration plus the minimum real-infra test needed to prove it

Incremental execution matters because assistants are strongest when each batch of work has a clear boundary and an immediate proof path. Large undifferentiated edits create two problems at once: they increase architectural drift and they make verification ambiguous.

The Execution Layer is therefore constrained by upstream layers. It does not decide architecture from scratch. It operates within the chosen workflow, stack grammar, archetype shape, manifest bundle, and canonical example posture. This is how the runtime preserves bounded autonomy. The assistant can move quickly, but only inside a constrained execution surface.

Execution also feeds downstream layers. Every code change, generated file, or updated configuration becomes input to verification. Every successful or failed validation becomes input to memory. The runtime is not complete until those transitions happen.

## Section 8 - Verification Layer

The Verification Layer makes correctness explicit. In this architecture, an implementation is not considered complete because it looks plausible. It is complete when the changed boundary has been proved at an appropriate level.

The repository supports several verification mechanisms:

- canonical example validation
- Docker-backed verification
- smoke tests
- scenario harnesses
- repo integrity checks
- script verification
- stack-specific example suites

Verification is essential because AI-generated artifacts are particularly vulnerable to confident but ungrounded correctness. A route may compile but not be wired into the app. A manifest may look coherent but point to stale files. A prompt sequence may look ordered while violating monotonic naming. A canonical example may appear authoritative while drifting from its stack guidance.

The verification architecture counters this by validating different kinds of truth:

- structural truth, such as manifest integrity, file presence, prompt numbering, and alias consistency
- behavioral truth, such as whether a route returns the expected result or a smoke path boots correctly
- runtime truth, such as whether Docker-backed systems actually build and answer a request
- reference truth, such as whether canonical examples still parse, import, mount, or execute through their scenario harnesses

Smoke tests play a specific role. They prove that the primary happy path or boot surface works. They are necessary but deliberately small. When a change touches real boundaries such as databases, caches, queues, search engines, or cross-service interactions, the runtime expects minimal real-infrastructure integration tests in addition to smoke coverage. This is a direct defense against hallucinated implementations that only work in mocked or imagined conditions.

Verification is therefore not a postscript. It is the layer that converts generated artifacts into runtime-trusted artifacts.

## Section 9 - Memory Layer

The Memory Layer maintains continuity across sessions without competing with code, doctrine, or manifests as a source of authority.

This layer is implemented through artifacts such as:

- `MEMORY.md`
- handoff snapshots
- architectural notes and operating documents that provide durable context for later sessions

Its job is to preserve operational state, not stable policy.

`MEMORY.md` is the runtime working-state artifact. It captures the current objective, active context, working set, inspected files, important findings, decisions already made, explicit non-goals, remaining risks, next steps, and the next meaningful stop condition. It exists so a fresh assistant session does not need to reconstruct the entire state of a live task from scratch.

Handoff snapshots serve a different purpose. They are durable point-in-time transfer artifacts for meaningful pauses, human review checkpoints, or assistant-to-assistant transitions. Where `MEMORY.md` is mutable and current, a handoff snapshot is fixed and archival.

This layer therefore distinguishes between:

- working memory, which is small, current, rewrite-friendly, and optimized for the next session
- archival knowledge, which captures durable checkpoints, transfer state, or stable architecture information

That distinction matters. If working memory becomes archival, it bloats and loses signal. If archival knowledge is missing, every transfer forces reconstruction and invites errors. The runtime separates these functions so continuity remains useful without becoming another uncontrolled context source.

The Memory Layer prevents several operational failures:

- repeated rescanning after interruptions
- forgotten decisions and scope boundaries
- vague handoffs between humans and assistants
- stale assumptions surviving across sessions without being made explicit

Memory does not override the rest of the runtime. The precedence remains code and tests first, doctrine next, manifests next, examples next, and memory as the current operational summary. This keeps continuity helpful without letting it bypass routing or proof.

## Section 10 - Cross-Layer Interaction

The runtime layers are useful individually, but the architecture only works because they interact through explicit control and feedback loops.

The basic forward path is:

1. intent defines the goal and constraints
2. planning converts the goal into a bounded work model
3. context routing selects the smallest justified active bundle
4. the knowledge layer supplies the governing rules and preferred patterns
5. execution produces code and operational artifacts
6. verification evaluates whether those artifacts actually satisfy the intended boundary
7. memory records the resulting operational state for the next cycle

The feedback path is equally important:

- intent influences planning because different goals produce different workflows, archetypes, and verification expectations
- planning influences context loading because the plan determines which workflow, stack, and archetype matter
- context influences execution because only the selected doctrine, examples, and patterns should dominate implementation
- execution produces artifacts that verification evaluates against real runtime boundaries
- verification results update memory by recording what passed, what failed, what remains, and which files matter next
- updated memory sharpens the next planning pass by reducing reload cost and preserving scope decisions

A concrete example makes the interaction clearer.

Suppose the human intent is to add a reporting endpoint to a backend service. Planning identifies the task as an API feature slice with smoke coverage. Context routing selects the backend API workflow, the repo’s dominant stack pack, the primary archetype, and one relevant canonical API example. The knowledge layer provides testing doctrine, naming guidance, stack grammar, and the preferred endpoint example. Execution adds the route and test. Verification proves app boot and the representative path. Memory then records the active files, the verification result, and the next step, such as adding an integration test if storage behavior is now in scope.

The same model applies to meta-repo tasks. If the human intent is to extend routing or add a new runtime rule, planning identifies a prompt-first repo maintenance path. Routing selects prompt-first doctrine, manifest logic, and repo bootstrap workflows. Knowledge retrieval loads the relevant docs and scripts. Execution updates router or manifest artifacts. Verification validates manifests, bootstrap invariants, or example integrity. Memory captures the new operational checkpoint.

This cross-layer loop is what prevents the system from behaving like a one-shot generator.

## Section 11 - Generated Project Repositories

`scripts/new_repo.py` is the mechanism that turns this base runtime into bounded execution environments for new projects.

Its role is architectural, not merely convenience-oriented. It creates descendant repositories that inherit the runtime model in a constrained form:

- a selected archetype
- a selected primary stack
- a selected manifest bundle
- generated entrypoint files such as `README.md`, `AGENT.md`, and `CLAUDE.md`
- a project profile manifest
- optional prompt files, smoke tests, integration tests, seed data, and deployment starters
- isolated Compose names, ports, env files, and volume roots

The important design property is boundedness. Generated repositories do not receive the entire meta-repo as active context. They receive only the scaffolding and context surfaces needed for the chosen project shape. This is why generated repos perform better for assistants: the runtime surface has already been narrowed at bootstrap time.

That boundedness improves assistant behavior in several ways:

- fewer competing stacks are present in the working repo
- archetype and workflow signals are clearer
- generated manifests and profiles provide a stable context entrypoint
- Compose isolation and validation expectations are explicit from the start
- smoke-test and integration-test expectations are built into the repo shape instead of added ad hoc later

In effect, `new_repo.py` compiles the general runtime into a project-local runtime with a smaller state space. The descendant repository is not just a code scaffold. It is a constrained operating environment for future assistant sessions.

## Section 12 - Autonomous Development Cycles

The runtime is designed to support long-lived development loops rather than isolated tasks.

The core autonomous cycle is:

`plan`
`-> execute`
`-> verify`
`-> update memory`
`-> refine plan`

This cycle is intentionally conservative. Each pass should stay within a bounded slice and end at a meaningful checkpoint. Verification is not deferred to the end of a giant batch. Memory is not deferred until everything is done. Refinement is not based on intuition alone; it is based on what verification and execution revealed.

Safe repetition of this loop depends on several runtime rules:

- planning must keep the next slice small and verifiable
- execution must not silently broaden scope into adjacent systems
- verification must match the changed boundary instead of using a generic “tests passed” claim
- memory must be refreshed at meaningful stop points so the next cycle starts from current operational state
- stop conditions must halt the loop when routing, verification, or safety boundaries become ambiguous

This is how the repository supports bounded autonomy. The assistant can sustain progress over many iterations, but each cycle is constrained by explicit routing, doctrine, and proof requirements. Autonomy is therefore operational, not unbounded.

## Section 13 - Multi-Agent Runtime Behavior

The runtime model also supports multiple assistants operating within the same architectural framework.

Multi-agent operation depends on explicit coordination mechanisms:

- worktrees
- branch isolation
- shared memory artifacts
- handoff snapshots
- merge checkpoints with defined integration authority

The architecture assumes that parallel work is only safe when conceptual boundaries are isolated. Separate assistants should operate on separate branches or worktrees when concurrent change surfaces could conflict. This reduces context complexity for each assistant and prevents two sessions from editing the same conceptual boundary without coordination.

Shared continuity artifacts are the logical counterpart to physical isolation. `MEMORY.md` acts as the canonical live-state summary for the current branch or integration checkpoint, while handoff snapshots preserve exact transfer state for a workstream or branch-specific checkpoint. In worktree-heavy operations, the system prefers branch-local or workstream-local handoff artifacts during divergence and a reconciled `MEMORY.md` at integration points.

This architecture enables parallel development streams because it separates:

- implementation autonomy from integration authority
- local workstream state from shared repo state
- narrow execution contexts from cross-cutting reconciliation work

The multi-agent model is therefore not “many assistants editing the same repo at once.” It is a coordinated runtime with isolation, explicit ownership, and shared continuity surfaces.

## Section 14 - System Design Principles

Several design principles explain why the runtime is structured this way.

Context discipline means the assistant should load only the files that answer the current decision. This prevents context bloat, example blending, and false thoroughness.

Deterministic workflows mean startup, routing, planning, and verification follow explicit sequences instead of ad hoc exploration. This improves reproducibility across sessions and assistants.

Verification-first engineering means code is not trusted because it looks correct. It becomes trustworthy only when the relevant structural, behavioral, or runtime checks pass.

Memory continuity means long-lived work is treated as a first-class operating condition. Current state must survive pauses without turning into an uncontrolled transcript.

Bounded autonomy means assistants are allowed to act quickly inside constraints, but they must stop on routing ambiguity, missing verification paths, or unclear safety boundaries.

Canonical pattern reuse means the system prefers verified reference implementations over improvised local conventions. This preserves architectural coherence as work accumulates.

Separation of authority means doctrine, manifests, examples, code, verification, and memory each keep distinct roles. No single artifact is allowed to become an unbounded substitute for the rest.

These principles are what make the repository useful as a runtime architecture instead of a generic best-practices collection.

## Section 15 - Future Evolution of the Runtime

The architecture is designed to scale as AI capabilities grow without losing its core discipline.

Several future directions fit naturally within this model.

Automated context routers can make task, stack, and archetype inference more robust and more explainable while still preserving explicit stop conditions and bounded bundle selection.

Agent scheduling systems can coordinate multi-agent work at the runtime level by assigning worktrees, verification targets, and integration checkpoints automatically rather than relying on manual orchestration.

Cross-repo orchestration frameworks can extend the same layered model beyond a single repository, allowing bounded continuity, verification, and handoff behavior across services while keeping each repo’s runtime state local and explicit.

Improved verification pipelines can raise the trust level of canonical examples, deployment surfaces, and generated descendant repos through richer harnesses, stronger Docker-backed checks, and better maturity metadata.

More formal context-budget tooling can make bundle approval even more deterministic by surfacing exact inclusion costs, ambiguity penalties, and escalation reasons during runtime operation.

The important point is that future evolution should add capability without collapsing the layers. More powerful assistants increase the need for runtime architecture because they can act more broadly and more quickly. As capability grows, the system must become more explicit about selection, proof, and continuity, not less.

`agent-context-base` is therefore a scalable runtime blueprint for AI-assisted development: a system that governs how intent becomes plan, how plan becomes bounded context, how bounded context becomes implementation, how implementation becomes verified behavior, and how verified state persists across sessions and operators.
