# Advanced Assistant Operations

This guide explains how expert operators should run long-lived, high-autonomy assistant workflows inside repositories derived from `agent-context-base`.

It assumes you already understand the basic planning and bootstrap workflow in `docs/usage/STARTING_NEW_PROJECTS.md`.

This document focuses on what happens after the repo exists and the work becomes operationally complex:

- long-running autonomous build sessions
- multi-agent execution
- bounded context expansion
- cross-repo coordination
- continuity across many sessions
- safe experimentation with higher autonomy

The core idea is simple:

Treat coding assistants as semi-autonomous engineering agents operating inside a constrained system, not as unstructured chat partners.

`agent-context-base` exists to make that operating model reliable.

## Section 1 - Why Advanced Operations Matter

Small AI coding sessions can succeed through momentum alone. Large ones usually cannot.

As soon as a project crosses a few boundaries such as multiple subsystems, multiple sessions, deployment wiring, test stacks, or several contributors, the failure mode changes. The problem is no longer "can the assistant write code?" The problem becomes "can the assistant keep making correct decisions after one hour, one interruption, one ambiguous request, and one partially completed verification cycle?"

Naive AI-assisted development usually degrades in predictable ways:

- context overload causes the assistant to load too many files, blur patterns, and lose dominance of the relevant stack or workflow
- hallucinated architecture appears when the assistant infers a repo shape from weak signals or blended examples
- drifting implementation plans emerge when the assistant keeps expanding the task instead of preserving a fixed objective
- memory loss between sessions forces later runs to reconstruct task state from code archaeology
- irreversible repository damage becomes more likely when broad edits, destructive commands, or speculative refactors are attempted without staged verification

Those failures are not random model defects. They are operational defects.

This repository mitigates them by separating concerns by authority and lifetime:

- doctrine defines durable rules
- workflows define execution procedures
- stacks define implementation families
- archetypes define repo shape
- manifests define bounded context bundles
- canonical examples define preferred patterns
- `MEMORY.md` preserves live task continuity
- handoff snapshots preserve durable transfer checkpoints

That separation matters because advanced assistant operations are mostly about controlling the order in which those layers are consulted.

An expert operator should expect the assistant to behave less like a conversational partner and more like a bounded engineering agent with these responsibilities:

- infer the active task without broad scanning
- load only the smallest justified context bundle
- declare stop conditions instead of inventing blended architecture
- implement in reviewable batches
- verify changed boundaries before claiming progress
- leave behind continuity artifacts that let the next session resume safely

If that sounds stricter than ordinary AI usage, that is the point. Long-lived autonomous work needs runtime discipline the same way distributed systems need failure handling.

## Section 2 - Long-Running Autonomous Build Sessions

Long-running autonomous sessions are useful when the task is large enough that constant operator intervention would reduce throughput, but narrow enough that one dominant workflow and one dominant stack can still govern the work.

The safest way to run them is to divide the session into explicit phases rather than one continuous coding stream.

### Planning Phase Versus Execution Phase

The planning phase should be short, explicit, and bounded. Its purpose is to answer:

- what is the exact objective for this run
- what workflow governs the task
- what files and boundaries are in scope
- what verification proves the change is real
- what is explicitly out of scope

The execution phase should only begin once those answers are concrete.

In this architecture, the planning phase should usually include:

1. boot sequence and repo-signal detection
2. reading `MEMORY.md` if present
3. selecting the dominant workflow, archetype, and stack
4. loading the minimal doctrine and one canonical example
5. defining the verification path before coding starts

If the plan cannot be stated cleanly, the assistant should not switch into long-running execution.

### Prefer Vertical Slices Over Horizontal Wandering

Long autonomous runs should move in vertical slices, not broad horizontal rewrites.

A vertical slice means one end-to-end increment that can be verified at the user-visible or system-boundary level. Examples:

- one endpoint plus smoke coverage plus required integration coverage
- one prompt sequence plus validation of numbering and references
- one pipeline step plus one tiny end-to-end transform check
- one deployment addition plus one boot-success verification path

This is better than horizontal work such as:

- editing five services before testing any of them
- touching router, schema, deployment, and docs together without proving the primary path
- refactoring shared abstractions before the first behavior is working

Vertical slices limit drift. They also create natural pause points for `MEMORY.md` updates and commit checkpoints.

### Commit Batching Discipline

Autonomous sessions should not accumulate a giant unreviewable diff.

Use commit batches that are:

- coherent enough to review
- reversible if the slice proves wrong
- small enough that the next session can understand the state quickly

In practice, a strong batch usually contains one of these:

- one feature slice
- one refactor plus its verification
- one docs or doctrine adjustment tightly coupled to the implementation change
- one verification harness addition

Avoid these patterns:

- "keep coding until the session ends"
- mixing unrelated cleanup into the active change
- bundling speculative architecture with proven behavior
- committing before verification status is known

The repository's commit hygiene doctrine exists for exactly this reason: advanced operations need commits that are easy to review, revert, and explain.

### Verification Checkpoints

A long autonomous session must periodically prove that it has not drifted away from reality.

Verification checkpoints should happen:

- after the first meaningful vertical slice
- before changing a storage, queue, search, or deployment boundary
- before and after a substantial refactor
- before each commit checkpoint
- before pausing the session

Use the repository's test philosophy:

- unit tests for local logic
- smoke tests for key happy paths
- minimal real-infra integration tests when real boundaries change

Use Docker-backed isolation when host tooling is absent or when boundary realism matters more than local convenience.

### Pause-And-Review Cycles

A multi-hour session should not stay in uninterrupted execution mode.

Insert pause-and-review cycles after every meaningful slice. At each pause, the assistant should:

1. restate the current objective
2. compare the live diff to the planned slice
3. rerun the defined verification path
4. inspect whether scope drift occurred
5. update `MEMORY.md`
6. decide whether to continue, checkpoint, or stop

These cycles are the operational equivalent of heartbeat checks. They keep autonomy bounded.

### Periodic Re-Evaluation During Long Sessions

During a long run, the assistant should periodically re-evaluate:

- whether the dominant workflow is still the right one
- whether the changed boundary still matches the original verification plan
- whether the active working set in `MEMORY.md` still reflects reality
- whether a fresh session would now be safer than continuing in the same one

This re-evaluation does not mean broadening context. It means checking whether the existing plan still holds.

### Updating `MEMORY.md` During Autonomous Runs

In long sessions, `MEMORY.md` should be updated at meaningful stop points, not after every command.

Useful updates include:

- what slice was completed
- which files are now in the active working set
- what was verified and what remains unverified
- what was intentionally deferred
- what exact next step should begin the next slice

Bad memory updates include transcripts, vague summaries, or stale next steps that no longer match the repo.

### When To Stop And Restart Fresh

Fresh sessions are often safer than heroic continuation.

Pause and restart with a fresh session when:

- the assistant has crossed several slices and the active context is becoming crowded
- multiple stop conditions have appeared in sequence
- the task boundary changed from feature work to deployment, storage, or architecture work
- repeated verification failures suggest the plan is wrong, not just incomplete
- the current session has accumulated too many inspected files and competing examples

A fresh session with a clean boot sequence, current `MEMORY.md`, and a handoff snapshot is usually higher quality than one more hour of context-saturated improvisation.

### Maintaining High Quality During Multi-Hour Runs

High quality in autonomous sessions comes from rhythm, not intensity.

The rhythm should be:

`plan narrowly -> implement one slice -> verify -> checkpoint -> compact memory -> continue only if the next slice is still clear`

That rhythm is what keeps long sessions from degrading into loosely guided code generation.

## Section 3 - Context Pruning Strategies

Context overload is one of the fastest ways to degrade assistant quality.

When assistants load too much context, several things happen at once:

- the dominant stack loses pattern authority
- examples start competing instead of guiding
- uncertainty is mistaken for permission to read more
- the assistant begins synthesizing composite architectures that the repo never intended
- previously sound implementation plans become noisy and unstable

This repository treats context management as an enforceable control problem, not a personal preference.

### Context Boot Sequences

The boot sequence exists to prevent arbitrary startup behavior.

For advanced work, keep the startup order deterministic:

1. read stable startup anchors and repo identity docs
2. inspect narrow repo signals
3. read `MEMORY.md` if it exists
4. read the latest relevant handoff snapshot only when clearly resuming a transfer
5. route the task through the routers
6. select the manifest or minimal bundle
7. load one dominant canonical example
8. begin work

The key property is that continuity artifacts are read early enough to reduce reload cost, but not so early that they replace routing and doctrine.

### Targeted Context Loading

Targeted loading means every file in the working context should answer one of these questions:

- what must remain true
- what sequence should be followed
- what stack grammar governs the touched surface
- what architecture shape is active
- what preferred pattern should dominate implementation

If a file does not clearly answer one of those, it is probably adjacent context rather than required context.

### Doctrine Selection Via Routers

Doctrine should not be loaded in bulk.

Instead, route into the smallest doctrine set that matches the changed boundary. Examples:

- naming and clarity doctrine for API and prompt changes
- smoke-test and testing doctrine for feature work
- Compose isolation doctrine for Docker-backed boundary work
- deployment doctrine only when deployment is actually changing
- stop conditions doctrine whenever ambiguity or escalation risk appears

The router system exists so assistants do not treat "read more philosophy" as a substitute for narrowing the task.

### Progressive Context Expansion

Expansion should happen in layers and only when earned.

A safe expansion pattern looks like this:

1. first-pass bundle with one workflow, one stack, one archetype, and one example
2. add one supporting doctrine file if a real boundary becomes active
3. add one supporting example only if it is orthogonal rather than competing
4. stop and re-evaluate before adding a second stack or second archetype

That progression preserves dominance.

### Explicit Context Eviction

Experts should actively evict context that is no longer useful.

Evict when:

- a phase is complete and its files are no longer in the active working set
- a competing example was inspected only for rejection
- a boundary such as deployment or storage proved irrelevant to the current slice
- prior exploration created ambiguity that the final plan resolved

In practice, explicit eviction means:

- rewrite `MEMORY.md` to match the current phase
- stop opening more adjacent docs from the previous phase
- start a fresh session when the loaded concepts have become too diverse

### The Context Complexity Budget

This repo's context complexity budget doctrine is the main control for advanced operations.

Treat context like a limited engineering budget with hard trade-offs:

- file count matters
- file size matters
- artifact type matters
- conceptual diversity matters
- stack count matters
- archetype count matters
- example count matters
- ambiguity should tighten the budget rather than expand it

The practical meaning is that not all "relevant" files should be loaded. Only the files that preserve the dominant pattern under the current task should be loaded.

### Practical Heuristics

Use these heuristics when deciding what to load:

- load files with direct authority over the current decision
- load one workflow before loading several neighboring workflows
- load one canonical example before comparing several near-matches
- load supporting stack packs only when the task activates those boundaries
- load deployment doctrine only when deploy behavior is changing

Use these heuristics when deciding what to defer:

- defer adjacent stacks that are merely plausible, not active
- defer deep example comparison until the primary pattern is insufficient
- defer deployment and observability material during local feature implementation unless the change crosses those boundaries
- defer broad refactor doctrine until the feature slice is proven

Use these heuristics when deciding what to summarize:

- summarize already inspected files that no longer need direct rereading
- summarize rejected options and why they were rejected
- summarize completed milestones into `MEMORY.md` or a handoff snapshot
- summarize historical rationale that still matters but no longer needs full narrative detail

Use these heuristics when deciding what to evict:

- evict obsolete next steps
- evict stale blockers
- evict working-set files from prior phases
- evict broad context acquired during exploration once the route is clear

An advanced operator should expect assistants to defend context choices explicitly:

Why this file, why now, what authority does it provide, and what higher-cost context was intentionally excluded?

## Section 4 - Safe YOLO Mode

YOLO mode in coding-assistant operations means granting the assistant higher execution autonomy with reduced step-by-step human supervision.

That phrase is useful only if it is defined carefully.

### Unsafe Autonomy

Unsafe autonomy looks like this:

- broad code changes without a bounded plan
- destructive commands issued for convenience
- architecture rewrites based on inference instead of repo evidence
- test avoidance because verification is slow or annoying
- multi-boundary edits without checkpointing
- silent continuation after ambiguous failures

Unsafe autonomy is not speed. It is unpriced operational risk.

### Bounded Autonomy

Bounded autonomy means the assistant can execute aggressively inside explicit constraints:

- fixed objective
- fixed repo surface
- declared stop conditions
- predefined verification path
- checkpoint discipline
- memory and handoff updates at pause points

This is the normal target state for advanced users.

### Safe YOLO Mode

Safe YOLO mode is bounded autonomy with more aggressive execution inside a pre-approved sandbox.

It is appropriate when:

- the task is narrow and reversible
- the dominant workflow and stack are already clear
- the verification harness exists or can be added quickly
- the operator wants throughput more than conversational control

It is not appropriate when:

- architecture is still undecided
- multiple stacks are equally plausible
- deployment or storage boundaries lack a minimal verification path
- the repo is already in a high-conflict or partially broken state

### How Safe YOLO Mode Should Operate In This Architecture

Inside an `agent-context-base` derived workflow, safe YOLO mode should still honor:

- the context boot sequence
- routers and manifest discipline
- stop conditions
- commit hygiene
- `MEMORY.md` updates at meaningful checkpoints
- handoff snapshots for major pauses
- smoke-test-heavy validation with minimal real-infra tests when boundaries matter
- Docker-backed isolation when real boundary verification needs it

In other words, safe YOLO mode is not "skip the process." It is "execute faster inside the process."

### Safeguards Required For Safe YOLO Mode

The minimum safeguard set should include:

- smoke tests for the main happy path
- verification harnesses that can be rerun quickly
- Docker-backed testing when host setup is unreliable or boundary realism matters
- commit checkpoints after each meaningful slice
- context budgeting to prevent runaway loading

If those safeguards do not exist, the assistant should spend part of the run creating them before increasing autonomy further.

### Gradual Escalation Of Autonomy

Do not jump from tightly supervised editing to wide-open autonomous execution.

Increase autonomy in steps:

1. supervised slice with explicit plan and visible verification
2. autonomous implementation of a second similar slice
3. autonomous verification and checkpointing inside the same boundary
4. only then limited broader runs across adjacent slices

This matters because most assistants become more reliable when they are allowed to repeat a validated pattern, not when they are asked to improvise across several new boundaries at once.

### Operational Rules For Safe YOLO Mode

Use rules like these:

- never run destructive commands without explicit justification
- never delete large sections of a repository without proving why the deletion is safe
- never change storage, queue, search, or deployment behavior without defining a verification path first
- always validate assumptions with tests when practical
- always checkpoint before crossing into a new operational boundary
- stop rather than blend patterns when routing ambiguity appears
- update `MEMORY.md` before pausing, even if the pause was unplanned

The point of safe YOLO mode is not fearlessness. It is disciplined speed.

## Section 5 - Multi-Agent Worktrees

Multiple assistants can collaborate effectively when their work is isolated physically and coordinated logically.

Git worktrees are a strong fit for that model because they let separate assistants operate on separate branches with separate checked-out directories while still sharing one repository history.

### Why Worktrees Help

Worktrees reduce context complexity by giving each assistant a narrower surface:

- one assistant sees only the frontend branch and files it needs
- another sees only the backend slice
- another works only on verification harnesses
- another focuses on docs or memory compaction

This is often better than one giant session trying to carry every concern at once.

### Typical Concern Splits

Common multi-agent splits include:

- frontend assistant
- backend assistant
- data-pipeline assistant
- verification-harness assistant
- documentation assistant

Each assistant should still use the same operating model:

- boot sequence
- routing
- bounded context
- canonical-example-first implementation
- verification checkpointing
- continuity artifacts

### Coordination Strategies

The most important coordination rule is to separate implementation autonomy from integration authority.

Use these strategies:

- shared `MEMORY.md` as the canonical live-state document for the current branch, but update it deliberately at merge checkpoints rather than letting every agent rewrite it continuously
- handoff snapshots per workstream or per checkpoint when one agent needs to transfer exact state to another
- branch conventions that make ownership obvious such as `feat/backend-report-endpoint`, `feat/frontend-dashboard-shell`, or `verify/search-integration-harness`
- merge checkpoints where one integration-focused session rebases, verifies, and reconciles competing edits

The phrase "shared `MEMORY.md`" needs discipline. In worktree-heavy operations, it should function as the canonical summary of current repo state, not as a constantly edited collaborative whiteboard. Use worktree-local notes or branch-local handoff snapshots during active divergence, then reconcile into `MEMORY.md` at agreed checkpoints.

### Recommended Worktree Pattern

A practical pattern looks like this:

1. create one integration branch that owns final merge and verification
2. create worktrees for isolated concerns
3. give each assistant a narrow objective and verification target
4. require each assistant to produce a small handoff snapshot before integration
5. merge one worktree at a time into the integration branch
6. rerun smoke and relevant integration tests after each merge checkpoint
7. update the canonical `MEMORY.md` after the integration checkpoint, not during every parallel substep

### How Worktrees Reduce Context Complexity

Worktrees are not just a Git convenience. They are a context-management tool.

They reduce complexity because:

- each assistant has fewer active files
- each branch usually has one dominant workflow
- examples stay more clearly aligned with the changed surface
- the integration session becomes the only place where cross-cutting concerns must be considered together

That last point matters. You do not want every assistant carrying full system context. You want one integration checkpoint carrying it intentionally.

### Conceptual Example

Imagine a repo adding a new reporting feature:

- worktree A adds the backend endpoint and smoke coverage
- worktree B adds the frontend report page and API wiring
- worktree C adds a PostgreSQL integration test because the report depends on query behavior
- worktree D updates docs and the operator runbook

Each assistant works in a narrow slice with its own branch and handoff snapshot.

Then an integration session merges:

1. backend first
2. verification harness second
3. frontend third
4. docs last

After each merge, the integration session reruns the relevant verification path and updates the canonical `MEMORY.md` with the new system state.

That pattern scales far better than one assistant trying to remember the entire full-stack change in one session.

## Section 6 - Repo-To-Repo Orchestration

Many real systems span multiple repositories:

- backend service repo
- data pipeline repo
- infrastructure repo
- observability repo
- prompt orchestration repo

`agent-context-base` supports this indirectly, not by acting as a central orchestration engine, but by giving every derived repo the same operating grammar:

- archetypes clarify repo shape
- stack packs clarify implementation families
- workflow doctrine clarifies execution sequence
- context discipline limits overload
- memory artifacts preserve continuity

That common grammar is what makes cross-repo work tractable.

### Core Principle

Do not run one assistant session as if all repositories were one giant codebase.

Instead, orchestrate across repos through bounded sessions with explicit handoffs.

### Recommended Cross-Repo Pattern

Use repo-specific sessions for repo-specific changes.

For example:

- session 1 in the backend repo defines the API contract and verification surface
- session 2 in the pipeline repo updates ingestion or transformation logic
- session 3 in the infrastructure repo adjusts Compose, secrets, or deploy wiring
- session 4 in the observability repo adds dashboards or alerts for the new surface

Each session should boot from that repo's own anchors, doctrine, and `MEMORY.md`.

### Cross-Repo Memory References

Cross-repo work still needs continuity, but continuity should be reference-based rather than context-loaded.

Good patterns:

- store concise cross-repo references in `MEMORY.md` such as "depends on contract in backend repo handoff snapshot `2026-03-13-report-api-contract.md`"
- maintain shared architecture documents that define stable contracts across repos
- create handoff snapshots that name exact external repo dependencies and validation status

Bad patterns:

- pasting large chunks of another repo's state into the current repo's memory
- loading several other repos' docs into one active session unless the task is explicitly integration-focused
- turning one repo's `MEMORY.md` into a multi-repo backlog

### Shared Architecture Documents

For larger systems, keep architecture coordination in stable shared documents rather than assistant memory alone.

Useful examples:

- API contract docs
- event schemas
- deployment topology docs
- observability expectations
- repo ownership maps

These documents reduce the need for assistants to infer cross-repo structure from transient chat history.

### Integration Checkpoints

Cross-repo work should converge through explicit integration checkpoints.

At each checkpoint:

1. reconcile contract changes
2. verify the affected repo independently
3. verify the cross-repo boundary with the smallest real integration path available
4. update repo-local `MEMORY.md` files to reflect the new external dependency state
5. write handoff snapshots if another repo or another session must continue

### How To Avoid Overwhelming Context

Use these rules:

- keep one repo as the active implementation surface in any one session
- reference other repos through contracts, snapshots, and concise memory notes
- switch repos when the dominant workflow changes
- reserve cross-repo sessions for integration validation and coordination work, not for broad implementation

The target is not omniscient assistant context. The target is coordinated bounded context.

## Section 7 - Advanced Memory Compaction Techniques

Long-running AI projects cannot keep all operational knowledge in live session context. They must compress.

This repository's memory layer exists to make that compression explicit and safe.

### Why Compaction Matters

Without compaction:

- `MEMORY.md` becomes a transcript
- old decisions remain mixed with live work
- stale blockers remain visible after they are resolved
- next steps no longer match the codebase
- future sessions reread too much and still miss the active objective

Compaction is what turns history into operationally useful continuity.

### `MEMORY.md` As A Persistent Knowledge Anchor

`MEMORY.md` is the repo's mutable current-state anchor.

It should preserve:

- the current objective
- active working set
- already inspected files that still matter
- current risks or blockers
- exact next steps
- explicit scope boundaries

It should not preserve everything the project ever did.

### Summarizing Completed Milestones

When a milestone is complete, compress it into a short operational statement.

For example:

- "report endpoint added, smoke test green, integration query test pending"
- "prompt batch 003 and 004 completed, numbering preserved, deployment prompt deferred"
- "test stack isolation fixed, host-port collision removed, rerun needed after merge"

That is enough to preserve momentum without carrying old narrative detail.

### Compressing Historical Decisions

Historical decisions should be rewritten into durable rationale, not copied forward as session chatter.

Good compressed forms:

- chose FastAPI pack because existing repo signals and canonical examples already dominate
- deferred Dokku doctrine because current slice is local-only and deploy wiring is unchanged
- rejected broad refactor because smoke coverage had not yet proven the new route behavior

This preserves why the decision was made without replaying the whole discussion.

### Storing Architectural Invariants

Some information should survive compaction because it constrains future work.

Good examples:

- "dev and test Compose names must remain repo-derived and distinct"
- "reporting queries require real PostgreSQL integration coverage"
- "prompt numbering remains monotonic; do not renumber completed prompt files"

Those are not transient notes. They are current invariants that future sessions must not violate.

### Maintaining Current Task State

The shortest useful memory is usually the best one.

A healthy `MEMORY.md` should let a fresh assistant answer quickly:

- what am I trying to finish
- what files matter next
- what is already proven
- what is still risky
- what should I do first

If a fresh assistant cannot answer those after reading `MEMORY.md`, the memory layer has not been compacted enough.

### Periodic Memory Rewriting

Do not append forever.

Assistants should periodically:

- rewrite `MEMORY.md` into current-state form
- remove obsolete blockers
- drop files from the working set that no longer matter
- collapse completed steps into milestone summaries
- move durable transfer details into handoff snapshots

The repository even provides a memory freshness checker because the system assumes growth pressure will otherwise make memory less useful over time.

### Archiving Obsolete Notes

When notes are historically useful but no longer belong in active memory, move them out.

Typical destinations:

- handoff snapshots for point-in-time transfer detail
- durable architecture docs for long-lived design rationale
- issue trackers or project docs for backlog items

Do not leave obsolete decisions in `MEMORY.md` just because they might be interesting later.

### Active Working Memory Versus Archival Design History Versus Handoff Snapshots

Keep these distinctions sharp:

- active working memory: mutable, current, optimized for immediate continuation
- archival design history: durable, explanatory, optimized for long-term understanding
- handoff snapshots: fixed checkpoints, optimized for transfer across sessions or assistants

When these layers blur, assistants either lose continuity or carry too much obsolete context.

## Section 8 - Handoff Snapshots

Handoff snapshots are the main tool for pausing and resuming advanced work safely.

They matter whenever a meaningful transition is about to happen:

- a fresh session will continue later
- another assistant will take over
- a human operator needs a precise checkpoint
- the current phase is complete and the next phase should start cleanly

### What A Good Handoff Snapshot Contains

A strong snapshot should include:

- current architecture state
- current task or phase
- completed work
- next tasks
- known risks and blockers
- exact files to inspect next
- verification status including what ran, what passed, what failed, and what was not run

When relevant, also include:

- active stack or archetype
- manifest or workflow used
- related external repo or contract references
- predecessor snapshot if this is part of a chain

### Why Snapshots Improve Resume Quality

Without snapshots, future sessions often pay a large restart tax:

- rereading many files to reconstruct where the last run stopped
- rediscovering rejected options
- re-running incomplete or irrelevant checks
- restarting from old architecture assumptions

A good snapshot collapses that restart tax into one bounded artifact.

### Snapshot Discipline

Snapshots should be:

- immutable once written
- timestamped
- concrete about file paths and validation state
- written at meaningful boundaries rather than after every tiny edit

They should not become narrative journals.

### Safe Pause Procedure

When pausing a session safely:

1. finish or explicitly abort the current micro-step
2. run the best available verification for the changed boundary
3. update `MEMORY.md` into current-state form
4. write a timestamped handoff snapshot
5. include exact next files and exact remaining risks

This is how you let the next session resume with bounded context rather than historical guesswork.

### Resume Procedure

When resuming:

1. run the normal boot sequence
2. read `MEMORY.md`
3. read the latest relevant handoff snapshot if this is clearly a transfer
4. verify that the codebase still matches the snapshot
5. continue only after reconciling any drift

Snapshots are transfer aids, not substitutes for inspecting the current repo state.

## Section 9 - Operating Multiple Sessions In Parallel

Expert operators sometimes run several assistant sessions at once:

- one planning session
- one implementation session
- one verification session
- one documentation session

This can increase throughput, but only if authority boundaries are clear.

### Session Roles

A useful pattern is to give each session a distinct role.

Planning session responsibilities:

- clarify scope
- track stop conditions
- decide next slices
- reconcile architecture decisions

Implementation session responsibilities:

- execute one narrow slice
- update code and tests
- checkpoint progress

Verification session responsibilities:

- run smoke tests, integration tests, and harness checks
- isolate failures from feature implementation noise
- produce precise verification summaries

Documentation session responsibilities:

- update operator docs, `MEMORY.md`, handoff snapshots, and runbooks
- avoid blocking implementation by batching narrative work separately

### Coordination Rules

To keep parallel sessions from conflicting:

- assign each session a narrow file ownership surface whenever possible
- prefer worktrees or separate branches for implementation-heavy sessions
- make one session the integration authority for merges and final verification
- reconcile `MEMORY.md` updates through checkpoints instead of free-form concurrent edits
- require each session to state exact files changed and exact verification run

### Avoiding Repository Conflicts

Parallel work breaks down when several sessions all believe they own the same conceptual boundary.

Avoid that by separating:

- architecture decisions from coding
- feature implementation from test harness work
- docs from moving implementation targets
- merge authority from parallel experimentation

If two sessions must touch the same files, they should probably not be running in parallel.

### Practical Parallel Pattern

A strong pattern for larger features is:

1. planning session defines the next two or three slices
2. implementation session handles the first slice
3. verification session validates the slice and prepares harness changes if needed
4. documentation session updates continuity artifacts after the checkpoint
5. planning session decides whether the next slice should proceed or stop

That gives you concurrency without surrendering control.

## Section 10 - Operational Checklists

Use these checklists as runbooks for advanced operations.

### Starting A Long-Running Session

- confirm the repo and task boundary
- run the boot sequence
- read `MEMORY.md` if present
- read the latest relevant handoff snapshot if resuming a transfer
- select one dominant workflow, stack, and archetype
- define one primary verification path
- define explicit stop conditions
- state what is out of scope for this run
- begin with one vertical slice, not a broad rewrite

### Pausing A Session Safely

- stop at a real boundary, not in the middle of a confused change
- run the best available verification for the touched surface
- note pass, fail, or not-run status explicitly
- rewrite `MEMORY.md` into current-state form
- create a handoff snapshot if another session may continue
- record exact next files and exact next step
- checkpoint or commit only if the batch is coherent and reviewable

### Starting A Safe YOLO Experiment

- verify the task is narrow and reversible
- confirm the dominant stack and workflow are already clear
- ensure smoke tests or a quick verification harness exist
- define destructive-command boundaries up front
- define when the assistant must stop instead of guessing
- require commit checkpoints after each meaningful slice
- keep the context bundle narrow even though autonomy is high

### Coordinating Multi-Agent Worktrees

- create one worktree per narrow concern
- assign one owner session for integration and merge authority
- give each assistant a separate branch and objective
- require a handoff snapshot or concise checkpoint summary from each worktree
- merge one worktree at a time
- rerun smoke and relevant integration checks after each merge
- update canonical `MEMORY.md` after integration checkpoints

### Performing Cross-Repo Orchestration

- keep one repo active per implementation session
- use shared architecture docs for stable contracts
- record cross-repo dependencies in memory and handoff artifacts concisely
- verify each repo locally before claiming system progress
- use integration checkpoints for cross-repo boundary validation
- avoid loading multiple repos' full context into one session unless the task is explicitly integration-focused

## Section 11 - Case Study Scenarios

The following scenarios show how these advanced techniques combine in practice.

### Scenario 1 - Building A Distributed SaaS Prototype

System shape:

- backend API repo
- frontend repo
- infrastructure repo
- observability repo

Recommended operation:

Start with repo-specific planning sessions. The backend session defines the first vertical slice such as account creation plus health checks. The frontend session waits until the backend contract is concrete rather than speculating early. The infrastructure session stays narrow, adding only the Compose or deploy isolation required to support the first slice. The observability session remains deferred until the service boundary is stable enough to instrument.

Use handoff snapshots to transfer API contract status between repos. Keep each repo's `MEMORY.md` local to that repo's current state. Use integration checkpoints only when the slice crosses repos meaningfully, such as frontend consuming the new backend endpoint.

Why the architecture helps:

- archetypes prevent each repo from pretending to be everything at once
- stack packs keep implementation style consistent per repo
- memory artifacts preserve continuity across many short sessions
- context budgets prevent one session from loading the entire SaaS system at once

### Scenario 2 - Expanding A Polyglot Backend Architecture

System shape:

- one repo with several services in different stacks
- shared storage and messaging boundaries
- growing test and deployment complexity

Recommended operation:

Do not treat this as a single undifferentiated coding session. Use worktrees by concern or service boundary. Let each assistant operate inside one dominant stack pack at a time. If one service is FastAPI and another is Go Echo, keep those in separate sessions or worktrees until integration time.

Require minimal real-infra integration tests for database, queue, or search changes. Use Docker-backed isolation aggressively because cross-service verification becomes unreliable when every host environment differs.

At the integration checkpoint, one session reconciles the service contracts and reruns cross-boundary verification. `MEMORY.md` should track only the current dominant workstream. Historical cross-service detail should move into handoff snapshots or architecture docs.

Why the architecture helps:

- the context complexity budget penalizes multi-stack drift
- stop conditions make it acceptable to pause instead of blending patterns
- canonical examples keep each service aligned to its own implementation family

### Scenario 3 - Creating A Multi-Language Canonical Example Suite

System shape:

- one prompt-first or meta repo
- many stacks
- examples, verification harnesses, manifests, and docs evolving together

Recommended operation:

Run one planning session that decides the next batch of example additions. Then run separate implementation sessions per stack family or per example family. A verification-focused session should own example registry updates and verification runs. A documentation session can update usage docs and example catalogs after the implementation proves out.

This is exactly the kind of work where context overload is dangerous. Do not keep multiple stack packs and multiple example families active in one session unless the task is explicitly comparative. Prefer one canonical example per family at a time. Use handoff snapshots to preserve which stacks are complete, which verification targets passed, and which gaps remain.

Why the architecture helps:

- manifests, example catalogs, and stack packs give structure to what would otherwise become a sprawling meta-repo
- memory compaction keeps the current example batch legible
- verification tooling keeps "canonical" from becoming a label without proof

### Scenario 4 - Developing A Data Pipeline Ecosystem

System shape:

- ingestion repo
- transformation repo
- analytics API repo
- observability or quality-check repo

Recommended operation:

Treat each repo as its own bounded implementation surface. The ingestion repo owns connector logic and tiny end-to-end ingest verification. The transformation repo owns schema normalization and deterministic fixture checks. The analytics API repo owns query endpoints and report verification. The observability repo stays focused on pipeline health signals rather than business logic.

Cross-repo continuity should flow through stable schemas, architecture docs, and handoff snapshots naming exact upstream and downstream dependencies. The most important operational habit is to validate each boundary separately before attempting system-wide runs.

If a schema or event contract changes, pause affected repos at their next checkpoint and update memory plus handoff artifacts so later sessions do not infer stale contracts.

Why the architecture helps:

- archetypes and stack packs keep ingestion, transformation, and API concerns distinct
- Docker-backed test isolation supports real boundary testing where mocks would hide failures
- repo-to-repo orchestration remains tractable because each repo shares the same operational grammar

## Closing Principle

Advanced assistant operations are not about making the assistant feel more human. They are about making the system behave more like disciplined engineering.

The highest-leverage habits are:

- narrow the task early
- preserve pattern dominance
- verify before claiming progress
- compact memory aggressively
- checkpoint before context degrades
- treat autonomy as something to bound, not something to romanticize

That is how `agent-context-base` turns autonomous assistant work from a fragile chat exercise into a repeatable operating model.
