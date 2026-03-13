# Starting New Projects

This guide explains how to use `agent-context-base` to move from a vague idea to a generated repository, then from a generated repository to repeatable autonomous build sessions.

The intended audience is both human operators and coding assistants. The goal is not just to start a repo quickly. The goal is to start it in a way that stays tractable after the first hour, the first interruption, and the fifth follow-up session.

## Section 1 - Purpose of `agent-context-base`

`agent-context-base` exists because naive AI coding sessions are easy to start and hard to sustain.

A naive session usually fails in one of a few predictable ways:

- it starts implementing before the project shape is clear
- it reads too much and loses pattern dominance
- it mixes examples from unrelated stacks
- it invents architecture because the request was vague
- it forgets the current state after a pause
- it keeps expanding context instead of narrowing decisions

This system exists to replace that behavior with a deterministic operating model:

`idea -> classification -> bounded context -> generated repo -> focused implementation -> verification -> continuity`

That operating model improves assistant workflows because it separates different kinds of knowledge by authority and lifetime.

### The Core Pieces

#### Context layers

The repository does not treat all guidance as the same kind of thing.

- doctrine contains durable rules and operating constraints
- workflows contain task procedures
- stacks contain implementation guidance for specific languages and frameworks
- archetypes contain project-shape guidance
- manifests assemble the smallest relevant bundle
- examples show preferred finished patterns
- templates provide scaffolding only
- memory artifacts preserve current task state between sessions

This matters because assistants reason better when stable rules, task playbooks, implementation patterns, and live working state are not blended together.

#### Context routers

Routers translate natural language and repo signals into a narrow working path.

- `context/router/task-router.md` maps requests to workflows
- `context/router/archetype-router.md` maps goals to project shape
- `context/router/stack-router.md` maps frameworks and file signals to stack packs
- `context/router/alias-catalog.yaml` normalizes synonyms and shorthand

Routers are the front door to discipline. They prevent the assistant from treating "I should read more" as a solution to uncertainty.

#### Archetypes

An archetype describes what kind of repository you are trying to create.

Examples in this base include:

- prompt-first repo
- backend API service
- CLI tool
- data pipeline
- local RAG system
- multi-storage experiment
- Dokku-deployable service

Archetypes answer "what shape is this repo?" before stacks answer "what framework is it built with?"

#### Stack packs

A stack pack describes the concrete implementation family. Examples include:

- Python + FastAPI + `uv` + Ruff + `orjson` + Polars
- Go + Echo
- Rust + Axum
- Elixir + Phoenix
- Scala + Tapir + http4s + ZIO
- Clojure + Kit + `next.jdbc` + Hiccup
- Kotlin + http4k + Exposed
- Nim + Jester + HappyX
- Zig + Zap + Jetzig
- Crystal + Kemal + Avram
- OCaml + Dream + Caqti + TyXML
- Dart Frog

Stacks answer "how should this kind of repo be built?"

#### Canonical examples

Canonical examples are verified reference implementations. They exist so the assistant does not improvise from scratch when a preferred pattern already exists.

Examples are higher authority than templates. A template helps start files. A canonical example helps shape the implementation correctly.

#### Verification layers

Verification makes examples trustworthy and generated repos safer to evolve.

The repository includes:

- manifest validation
- routing and integrity checks
- script verification
- example verification
- Docker-backed runtime verification for stacks where host toolchains may be absent

This is important because an unverified example becomes a drift multiplier.

#### Memory checkpoints

Long-running work needs continuity. This system uses:

- `MEMORY.md` for mutable current-task state
- handoff snapshots for durable transfer checkpoints
- stop hooks for routine end-of-phase continuity updates

These artifacts keep a future session from having to reverse-engineer where the last session stopped.

#### Context complexity budgeting

Context discipline is not just style guidance in this repo. It is an operating principle.

The budget model exists because assistants degrade when they load too many files, too many concepts, or too many competing examples. The right response to ambiguity is usually to stay narrow, not to broaden the bundle.

### How The Pieces Interact

The system should be thought of as a narrowing pipeline:

1. Start with a rough idea.
2. Use routers to infer the dominant task, archetype, and stack.
3. Let a manifest define the smallest relevant context bundle.
4. Use doctrine to constrain behavior.
5. Use one workflow to sequence the work.
6. Use one canonical example to shape implementation.
7. Verify the result.
8. Preserve continuity with memory artifacts before pausing.

That sequence is what makes the system reusable. It reduces arbitrary browsing, arbitrary coding, and arbitrary forgetting.

## Section 2 - The Two-Repo Model

The most important operating concept in this repository is the two-repo model.

### Repo 1: `agent-context-base`

This repo is the control tower.

It is where you:

- classify vague ideas
- choose archetypes and stacks
- inspect manifests
- study routers and canonical examples
- preview context bundles
- generate a new repo with `scripts/new_repo.py`

It is not where most product implementation should happen.

### Repo 2: The Generated Project Repo

The generated repo is the worksite.

It is where you:

- implement product behavior
- add project-local manifests and examples
- write real application code
- run repo-specific smoke and integration tests
- evolve memory checkpoints across build sessions

The base repo should remain a reusable operating system. The generated repo should become the project.

### Why The Separation Matters

If you build the actual product inside `agent-context-base`, several bad things happen quickly:

- the base accumulates product-specific noise
- routing becomes less general and less trustworthy
- examples and templates become blurred with app code
- future project generation becomes harder
- assistants have more context to filter before they can reason cleanly

The base repo is optimized for planning and bounded generation. Generated repos are optimized for implementation and iterative delivery.

### Planning Versus Building

Treat work in two phases:

#### Planning phase

Use `agent-context-base` to answer:

- what kind of project is this?
- what stack is most appropriate?
- what is the smallest useful repo profile?
- which manifests and workflows matter?
- what should `new_repo.py` receive?

#### Building phase

Use the generated repo to answer:

- what is the first vertical slice?
- what code, tests, and deployment wiring are needed?
- what memory checkpoints should survive the next pause?
- what verification proves this change is real?

Planning is classification and narrowing. Building is implementation and proof.

## Section 3 - The Ideal Workflow

The ideal lifecycle is intentionally staged.

### 1. Start with a vague idea

Begin with a short description of the problem, intended user, rough constraints, and any suspected stack directions.

Do not wait until the idea is fully specified. The system is designed to help classify ambiguity, not just accept already-finished specs.

### 2. Start an assistant session in `agent-context-base`

Open a fresh session in this repo, not in an empty directory and not in an old unrelated project repo.

This gives the assistant access to:

- routers
- archetypes
- stack packs
- manifests
- examples
- verification docs
- repo generation tooling

### 3. Use planning mode

Ask the assistant to classify and plan before generating anything.

The first goal is not "write code." The first goal is "identify the repo shape, stack, verification posture, and smallest useful initial profile."

### 4. Classify the idea

Ask what kind of system the vague idea seems to be.

Examples:

- backend service
- CLI tool
- data pipeline
- local RAG system
- prompt-first meta repo
- multi-storage experiment

The classification should be explicit, even when tentative.

### 5. Determine the archetype

Pick one primary archetype.

If two archetypes seem plausible, force the decision early. For example:

- "backend API service" versus "Dokku-deployable service"
- "data pipeline" versus "CLI tool"
- "local RAG system" versus "multi-storage experiment"

Choose the shape that best matches the user-visible goal. Do not carry multiple primary archetypes unless the repo is intentionally composite.

### 6. Determine the stack

Select one primary stack and, only if justified, one or two supporting stacks.

Examples:

- FastAPI for HTTP plus Redis for caching
- Go + Echo for service surface plus Postgres for persistence
- DuckDB + Trino + Polars for analytical pipeline work
- Qdrant for local retrieval in a RAG system

The assistant should recommend a default stack and at least one plausible alternative when tradeoffs are real.

### 7. Determine the minimal context subset

Before generation, identify the smallest set of context surfaces that matter:

- one primary workflow
- one primary archetype
- one primary stack
- one preferred canonical example
- only the doctrine relevant to repo generation and the intended first slice

This is where context complexity budgeting starts paying off. You are not trying to preload the future project. You are trying to generate a clean starting repo.

### 8. Generate arguments for `new_repo.py`

Convert the planning output into concrete arguments.

Typical outputs include:

- repo name
- `--archetype`
- `--primary-stack`
- `--manifest` entries if needed
- `--smoke-tests`
- `--integration-tests`
- `--seed-data`
- `--dokku`
- `--prompt-first`
- `--docker-layout`
- optional `--target-dir`

At this point the assistant should be able to explain every flag.

Useful checks before generation:

```bash
python scripts/new_repo.py --list-archetypes
python scripts/new_repo.py --list-stacks
python scripts/new_repo.py --list-manifests
python scripts/preview_context_bundle.py <manifest-name> --show-weights --show-anchors
```

Those commands are useful when the planning session is down to one or two likely profiles and you want to inspect the bundle before creating a repo.

### 9. Run `new_repo.py`

Generate the repo from the base rather than manually copying files.

Conceptually:

```bash
python scripts/new_repo.py my-new-project \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data \
  --dokku
```

The exact flags should come from the planning pass, not from habit.

If you want one last sanity check before writing files, use a dry run first:

```bash
python scripts/new_repo.py my-new-project \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data \
  --dokku \
  --dry-run
```

### 10. Create a bounded repo

The generated repo should be intentionally small.

A good generated repo contains:

- the right routing entrypoints
- the relevant docs and templates
- the smallest useful Compose and test posture
- the right starter tests and scaffolding

It should not contain every context file from the base.

### 11. Start a fresh assistant session in the generated repo

Do not continue the main build inside the base repo session.

Open a fresh session in the new project repo so the assistant can reason from the bounded project surface rather than from the full control tower.

### 12. Run the boot sequence

In the generated repo, start with the repo's own startup path:

1. `README.md`
2. `docs/context-boot-sequence.md`
3. `docs/repo-purpose.md`
4. `docs/repo-layout.md`
5. the task router
6. `MEMORY.md` if present

This preserves the same disciplined startup model in descendant repos.

### 13. Begin vertical slice development

Start with one meaningful vertical slice, not an abstract architecture pass.

Examples:

- one health endpoint plus one representative route
- one CLI command plus one smoke check
- one pipeline step plus one deterministic fixture
- one retrieval path plus one minimal round-trip verification

The first slice should prove repo viability, not solve the entire roadmap.

### 14. Use memory checkpoints

Initialize and maintain `MEMORY.md` when the task is non-trivial or likely to span sessions.

Use it to record:

- current objective
- active working set
- decisions made
- blockers
- next steps
- validation state

### 15. Use stop hooks

Before pausing after meaningful work, update `MEMORY.md` and create a handoff snapshot when the pause is likely to cross sessions, assistants, or humans.

Do this especially when:

- architecture has just been clarified
- code changed but tests are still pending
- smoke tests failed and the failure now shapes the task
- a major subtask completed

### 16. Use context complexity budgeting

During implementation, keep each session bounded:

- load the smallest relevant doctrine
- use one workflow at a time
- use one preferred example at a time
- do not preload unrelated stack packs
- only escalate context when the task activates a new boundary

### 17. Use handoff snapshots

When work will continue later, write a durable snapshot under the repo's handoff location.

Snapshots are especially useful for:

- long-running project setup
- deployment hardening
- storage integration work
- prompt-first repos with numbered prompt batches

### 18. Continue iterative sessions

Repeat the same cycle in bounded increments:

`boot -> inspect current memory -> load minimal context -> implement one slice -> verify -> stop hook`

That rhythm consistently outperforms one giant monolithic session because:

- each session starts from a smaller, cleaner context
- decisions are made earlier
- verification is closer to the change
- memory artifacts reduce reload cost
- the assistant has fewer opportunities to blend patterns or invent structure

Multiple bounded sessions are not a compromise. In this architecture they are the intended operating mode.

## Section 4 - How Context Complexity Budgeting Works

Assistants degrade under context overload for two separate reasons:

- token volume grows
- conceptual diversity grows

The second problem is often worse than the first. A bundle can be short and still be cognitively bad if it mixes too many competing ideas.

### Why Overloaded Assistants Fail

When too much context is loaded, assistants tend to:

- flatten authority boundaries
- mix templates with canonical examples
- import patterns from adjacent stacks
- treat optional docs as required
- forget which files are actually active
- answer uncertainty by reading more files instead of resolving the decision

This system counters that with a budgeting layer between routing and loading.

### What The Budgeting System Does

Conceptually, the budget system asks:

- what is the dominant task?
- what is the dominant archetype?
- what is the dominant stack?
- what files are required for that path?
- what optional files are actually justified now?
- what should remain excluded unless the task expands?

The result should be a first-pass bundle, not an exhaustive bundle.

### How Context Routers Help

Routers reduce ambiguity before files are loaded.

For example:

- if the request is "set up a small analytics API," the task router points toward repo bootstrap, the archetype router points toward backend service, and the stack router may point toward FastAPI
- if the request is "build a local question-answering tool over my docs," the archetype router points toward local RAG, and the stack router may point toward Qdrant instead of unrelated search systems
- if the request is "compare Redis and Mongo behavior," the archetype router points toward multi-storage experiment rather than a normal backend service

Routing first means the assistant does not need to open every stack or every example to discover what matters.

### How Assistants Should Reason About Loading Context

A good internal loading sequence looks like this:

1. Load startup anchors and repo identity.
2. Resolve the task.
3. Resolve the archetype if project shape matters.
4. Resolve the stack on the active surface.
5. Choose the best manifest.
6. Load required context only.
7. Add one preferred example.
8. Escalate only if the change crosses a real new boundary.

### Conceptual Example 1: Small FastAPI Service

The user wants a lightweight internal analytics API.

A bad bundle would include:

- all backend stacks
- all deployment docs
- all storage docs
- multiple API examples from other ecosystems

A good first-pass bundle would include:

- bootstrap workflow
- backend API archetype
- FastAPI stack pack
- one FastAPI canonical example
- only the doctrine relevant to testing and repo generation

Redis, Dokku, and seed-data guidance can wait unless the plan explicitly activates them.

### Conceptual Example 2: Prompt-First Research Repo

The user wants a repo to manage prompts, research notes, and staged task batches.

A bad bundle would include backend service doctrine, storage packs, and runtime API examples.

A good first-pass bundle would include:

- prompt-first archetype
- prompt-first stack pack
- bootstrap workflow
- prompt conventions
- one canonical prompt layout example

The project stays legible because the system did not preload unrelated service patterns.

### Conceptual Example 3: Local RAG Experiment

The user wants a local document index with deterministic retrieval.

A bad bundle would load Elasticsearch, Meilisearch, MongoDB, Postgres, and general backend API patterns all at once.

A good bundle would start with:

- local RAG archetype
- Qdrant stack pack
- local RAG workflow
- one local RAG canonical example
- only the verification and storage context needed for the first retrieval slice

The broader search ecosystem should remain excluded until the project intentionally becomes comparative.

## Section 5 - Role of `MEMORY.md` and Stop Hooks

`MEMORY.md`, handoff snapshots, and stop hooks are what make this architecture viable across real interrupted work.

Without them, every fresh session pays a reconstruction tax.

### `MEMORY.md`

`MEMORY.md` is the mutable current-state artifact for the live task.

It should stay small and operational. It should normally contain:

- current objective
- active working set
- important findings
- decisions already made
- explicitly not doing
- blockers or risks
- next steps
- validation status

It is not a transcript, backlog dump, or substitute for doctrine.

### Handoff Snapshots

Handoff snapshots are durable point-in-time records.

Use them when:

- the work will continue in a later session
- another assistant may continue
- a human may take over
- a major checkpoint is worth preserving

Keep snapshots fixed. Keep `MEMORY.md` rewrite-friendly.

### Stop Hooks

A stop hook is the small continuity action performed before pausing after meaningful work.

In practice, a stop hook usually means:

1. update `MEMORY.md`
2. prune stale notes
3. record exact next files or validations
4. create a handoff snapshot if the pause is durable

### When To Update Memory

Update `MEMORY.md` when:

- the task is midstream
- code changed but validation is pending
- architecture has been clarified
- failing tests now shape the next step
- the same task will continue later

### When To Snapshot State

Create a handoff snapshot when:

- the session is ending for the day
- another operator will continue
- a major subtask just completed
- the project now has a checkpoint worth preserving

### When To Compact Context

Compact rather than append when:

- completed next steps are no longer relevant
- blockers have been resolved
- the active working set has narrowed
- old notes would force future sessions to scan history

Good memory reduces reload cost. Bad memory becomes another source of context sprawl.

## Section 6 - Canonical Examples and Verification

Canonical examples exist because assistants generate better code when they are asked to extend a proven pattern rather than invent a fresh one under weak constraints.

### Why Canonical Examples Exist

They serve three practical purposes:

- accelerate onboarding to a stack
- provide a preferred implementation shape
- reduce hallucinated pattern mixing

They are especially valuable in multi-language environments because the assistant can align to a verified local pattern instead of relying on generic model memory.

### How They Accelerate Stack Onboarding

A new repo or a new operator can inspect one well-chosen example and quickly understand:

- route layout
- service boundaries
- test shape
- deployment posture
- fixture expectations
- naming conventions

That is much faster and safer than inferring the pattern from scattered docs.

### How They Enable Reliable Generation

When the assistant chooses one direct example:

- file shape becomes clearer
- naming becomes more consistent
- test structure becomes easier to reproduce
- verification expectations become more concrete

The system intentionally prefers one direct example over blended hybrids because blended examples are a common source of invented architecture.

### Why Verification Matters

Examples are only useful if they remain trustworthy.

This repo therefore verifies examples at multiple levels:

- structural integrity
- syntax or parse checks
- smoke verification
- behavioral verification where feasible
- Docker-backed runtime verification for heavier stacks

### The Docker Verification Strategy

Many stacks in this ecosystem are valid but not installed on every machine. Docker-backed verification solves that operational problem.

It lets the repository prove:

- a canonical example builds
- a service boots
- a minimal request path works

without requiring every operator to install every language toolchain locally.

That matters for long-term reuse because the examples remain practical across diverse environments, not just on one author's machine.

## Section 7 - The Role of `new_repo.py`

`scripts/new_repo.py` is the bridge between planning and execution.

It should be thought of as a repo generator for bounded descendants, not as a generic project factory.

### What `new_repo.py` Does

At a high level it:

- accepts a repo name, archetype, and primary stack
- maps those choices onto known manifests
- selects relevant scaffolding
- creates a focused starter repo
- optionally adds smoke tests, integration tests, seed data, Dokku files, and prompt-first assets
- writes a generated profile so the resulting repo is inspectable

### How It Subsets Context

It does not copy the entire base repo. It generates only the surfaces justified by the chosen profile.

That is one of its most important jobs. Noise reduction is a feature, not a side effect.

### How It Selects Archetypes

The `--archetype` flag declares repo shape.

Examples:

- `backend-api-service`
- `cli-tool`
- `data-pipeline`
- `local-rag-system`
- `multi-storage-experiment`
- `prompt-first-repo`
- `dokku-deployable-service`

This tells the generator what kind of repo it is trying to create before framework details are applied.

### How It Selects Stacks

The `--primary-stack` flag selects the dominant implementation family.

That choice determines starter directory layout, stack-aware file hints, and related defaults.

Supporting stacks can be brought in later at the project level if the work truly activates them.

### How It Selects Workflows

`new_repo.py` is not itself the workflow selector, but it is downstream of workflow selection.

In practice:

- the planning session uses router and manifest logic to decide the dominant workflow and profile
- the planning output becomes concrete `new_repo.py` flags
- the generated repo then carries the smallest useful workflow and scaffolding surface forward

### How It Prepares Scaffolding

Depending on flags, it can prepare:

- README and assistant entrypoints
- Compose files
- starter smoke tests
- starter integration tests
- seed-data scripts
- prompt-first files
- Dokku deployment docs and artifacts

This should be treated as initial structure, not as finished architecture.

### How It Reduces Noise

The script exists partly to protect future sessions from overload.

A descendant repo should not begin life with:

- every stack pack
- every example category
- every template
- every doctrine file

It should begin with the smallest profile that makes the project buildable.

### How To Use It After Planning

The right workflow is:

1. run a planning session in `agent-context-base`
2. decide archetype, stack, deployment posture, and verification needs
3. translate those decisions into flags
4. run `new_repo.py`
5. start the real build in the generated repo

Do not skip the planning pass and use `new_repo.py` as a guessing tool.

### Useful `new_repo.py` Habits

Use these habits consistently:

- use `--list-archetypes`, `--list-stacks`, and `--list-manifests` when the planning output needs a quick reality check
- use `--dry-run` when the repo profile is almost settled but you want to inspect the planned output first
- use `--target-dir` when the repo should be created somewhere other than `./<repo-name>`
- add optional flags only when the first slice truly needs them

The generator is most effective when it turns a clear planning decision into a clean bounded repo, not when it is used to explore possibilities by trial and error.

## Section 8 - Recommended Session Pattern

The best operating rhythm is:

`Planning Session in base repo -> Implementation Session in generated repo`

### Planning Session

Run this in `agent-context-base`.

Primary goals:

- classify the project
- choose the archetype
- choose the stack
- identify the first verification posture
- decide the minimal repo profile
- produce `new_repo.py` arguments

The planning session should stay analytical and narrow. It should not drift into building the app in the base repo.

### Implementation Session

Run this in the generated repo.

Primary goals:

- run the boot sequence
- define the first vertical slice
- implement
- verify
- update memory artifacts
- hand off cleanly

### Plan Mode

Use plan mode when:

- the idea is still vague
- multiple archetypes are plausible
- stack choice affects repo shape materially
- deployment posture is unclear
- the first slice is not yet obvious

Plan mode is classification-heavy and code-light.

### Bounded Autonomy

Bounded autonomy is the default build posture once the repo exists.

It means the assistant has freedom to:

- inspect the necessary code
- make targeted changes
- run relevant verification
- update memory artifacts

but only within a clearly defined slice and context budget.

This is the safest and most productive mode for most work.

### Yolo Mode

Use yolo mode sparingly.

It is appropriate when all of the following are true:

- the scope is narrow
- the stack and archetype are already settled
- verification is straightforward
- the blast radius is low
- the repo is already well-bounded

Examples:

- adding a small smoke test
- wiring a single simple endpoint in an already-classified repo
- fixing a localized prompt filename or helper script issue

It is not appropriate for:

- first-time repo classification
- large architecture decisions
- multi-storage integration
- deployment rewiring
- anything that would encourage broad exploratory loading

## Section 9 - Ideal Initial Prompt Strategy

The first prompt matters because it shapes the assistant's early routing decisions.

The best initial prompt is usually 2 to 5 sentences.

That is enough space to communicate intent without flooding the assistant with speculative detail.

### What The First Prompt Should Include

It should usually include:

- the vague idea
- who it is for or what problem it solves
- meaningful constraints
- possible stack hints if they exist
- deployment expectations if known
- an explicit request for planning-mode classification

### Why 2 To 5 Sentences Is Usually Ideal

Very short prompts often omit constraints that matter for archetype choice.

Very long prompts often include premature architecture and irrelevant detail, which can bias the assistant toward over-building.

Two to five sentences usually preserves the right amount of ambiguity:

- enough detail to classify
- not so much detail that the repo shape is overfit too early

### What Information Helps Assistants Reason Well

Useful inputs:

- "internal tool" versus "small SaaS" versus "personal utility"
- expected users or operators
- likely data sources or storage needs
- whether the project is interactive, batch, or API-driven
- whether deployment matters now
- rough language preferences
- whether local-only or Docker-backed operation is preferred

Useful requests:

- "classify the project archetype"
- "recommend a primary stack and one alternative"
- "suggest the smallest repo profile"
- "produce `new_repo.py` arguments"

### A Strong First Prompt Pattern

Use a prompt shaped like this:

> I have a rough idea for a project that does X for Y. I think it might want stack A or B, and I expect deployment posture C. Please treat this as a planning session: classify the archetype, recommend the best initial stack, suggest the smallest repo profile, and give me `new_repo.py` arguments.

That format creates a clean handoff into the system's routing model.

## Section 10 - Example Planning Output

A good classification response should not jump straight to code. It should convert ambiguity into a usable repo-generation decision.

Good planning output usually contains:

- inferred archetype
- recommended primary stack
- plausible alternative stack
- recommended workflows
- suggested repo profile or manifest set
- first verification posture
- `new_repo.py` arguments

### Example

```text
Project read:
- This looks like a backend API service with a likely Dokku deployment posture.
- The dominant goal is serving a small analytics API, not building a general data platform.

Recommended archetype:
- backend-api-service

Recommended primary stack:
- python-fastapi-uv-ruff-orjson-polars

Alternative stack:
- go-echo
- Better if you want a smaller runtime and simpler static deployment story, but weaker if Polars-heavy data shaping is a near-term need.

Recommended workflows:
- bootstrap-repo
- add-api-endpoint
- add-smoke-tests
- add-storage-integration only after the first storage-backed route exists

Suggested repo profile:
- Start from the FastAPI backend manifest
- Include smoke tests, integration tests, seed data, and Dokku posture
- Keep Redis or analytical storage out of the first generated surface unless the first slice needs it

Proposed `new_repo.py` command:
python scripts/new_repo.py tenant-analytics-api \
  --archetype backend-api-service \
  --primary-stack python-fastapi-uv-ruff-orjson-polars \
  --smoke-tests \
  --integration-tests \
  --seed-data \
  --dokku

First implementation slice after generation:
- health route
- one report summary endpoint
- one smoke test
- one Docker-backed integration test only if persistence is introduced immediately
```

That kind of output is strong because it makes the next action obvious and keeps the first repo profile intentionally small.

## Section 11 - Anti-Patterns

These mistakes reliably reduce the quality of generated projects and later assistant sessions.

### Starting implementation inside `agent-context-base`

This confuses the control tower with the worksite. It pollutes the reusable base with project-specific code and makes future classification noisier.

### Loading excessive context

Reading many files can feel careful while actually making the assistant less precise. Excess loading weakens pattern dominance and increases contradiction risk.

### Skipping classification

If you generate or code before choosing archetype and stack, the first session often invents a repo shape accidentally. Later sessions then inherit a weak foundation.

### Not using memory artifacts

Long-lived work without `MEMORY.md` or snapshots forces every new session to reconstruct state. That wastes context budget and increases drift.

### Running huge monolithic sessions

Large uninterrupted sessions create invisible state that is hard to transfer cleanly. Bounded sessions with stop hooks preserve more reliable continuity.

### Mixing verification infrastructure into project repos unnecessarily

Generated repos should inherit the verification posture they need, not the entire verification machinery of the base. Keep the descendant repo focused on its own smoke and integration needs.

### Treating templates as canonical architecture

Templates are there to scaffold. Canonical examples and actual project code should define the real shape.

### Loading multiple near-match examples

If the assistant cannot name the one dominant example, it is already at risk of blending patterns.

### Carrying every possible future dependency into the first repo

Do not preload Redis, MongoDB, vector search, Dokku, analytics storage, and prompt orchestration unless the first phase truly needs them. Future capability is not a reason to widen the initial repo.

### Letting `MEMORY.md` become an archive

When memory becomes a transcript, it stops reducing context cost and starts adding it.

## Section 12 - 50 Example Initial Prompts

These prompts are intentionally concise, realistic, and planning-oriented. Each is suitable for starting in `agent-context-base` and asking the assistant to classify the project before generation.

### 1.

I want a small internal service that shows which background jobs are stuck, retrying, or silently failing across a few teams. Python with FastAPI seems plausible, but Go with Echo might also work if it keeps the service lean. Please treat this as a planning session and classify the archetype, recommend the best starting stack, and give me `new_repo.py` arguments.

### 2.

I have an idea for a CLI that scans a repo and tells me whether an assistant session is drifting from the dominant stack and archetype. Rust with Axum is probably overkill unless a tiny local web report helps, so I am not sure if this should stay a pure CLI tool or become a small developer dashboard. Classify it first and suggest the smallest repo profile.

### 3.

I want to build a lightweight API that lets recruiters upload job descriptions and get normalized skill tags plus seniority guesses. FastAPI feels likely because Python NLP tooling is convenient, but I care about keeping the first repo very small. Please classify the project, recommend a stack, and outline the generation command.

### 4.

I am considering a local RAG tool that indexes a folder of engineering RFCs and answers questions with citations. Qdrant seems like a good fit, but I want the first version to stay deterministic and Docker-backed. Please plan the repo shape and generate the initial `new_repo.py` flags.

### 5.

I want a service that receives webhook events from several systems and turns them into a unified activity feed for internal ops use. Go with Echo or Kotlin with http4k both seem reasonable, and Dokku deployment is likely. Please classify the archetype, pick a preferred stack, and propose the minimal starting repo.

### 6.

I have a vague idea for a data pipeline that pulls CSV exports from a few vendors, normalizes them, and produces a clean analytics table every morning. DuckDB plus Trino plus Polars sounds right, but I want help deciding whether this should begin as a pipeline repo or a backend service. Please classify first and give me the generator arguments.

### 7.

I want a personal productivity tool that turns meeting notes into a daily action digest and a weekly review summary. It might begin as a CLI, but I could imagine a tiny API later for integrations. Please keep the planning conservative, choose the archetype, and recommend the smallest useful generated repo.

### 8.

I want to experiment with comparing Redis, KeyDB, and MongoDB for storing ephemeral document-processing state. This is more of a learning and benchmark repo than a product, and I do not want the assistant to assume a normal backend service shape. Please classify it and suggest the right manifest profile.

### 9.

I want an internal dashboard that shows which APIs are missing smoke tests, deployment notes, or owner metadata. Elixir Phoenix could make the operator UI pleasant, but a Go Echo service might be easier to keep lean. Please treat this as planning, recommend an archetype and stack, and produce `new_repo.py` arguments.

### 10.

I want a tool that reads a folder of invoices and contracts, extracts dates and payment terms, and exports a searchable ledger. Python feels likely because of document tooling, but I am unsure whether to frame this as a CLI-first document processor or a backend API from day one. Please classify and suggest the initial repo shape.

### 11.

I want a tiny SaaS concept for teams that need a shared release checklist with environment-specific approvals and deployment evidence. A backend API plus a simple front-end surface is enough for now, and Dokku deployment is likely. Please classify it, recommend the best starting stack, and keep the initial repo bounded.

### 12.

I want a prompt-first repo that organizes recurring research tasks, experiment prompts, and numbered follow-up prompts for a small AI tooling team. It should stay explicit and easy for multiple assistants to continue later. Please classify it as a planning exercise and give me the right `new_repo.py` setup.

### 13.

I want a developer tool that watches a running service's logs and summarizes the top recurring structured error shapes over the last hour. Rust or Go seem plausible, but if a lightweight Python service makes the first version faster I am open to that. Please classify the project and recommend the smallest useful repo profile.

### 14.

I want a backend that lets job seekers store application links, interview stages, notes, and follow-up reminders. Python FastAPI seems fine, though Kotlin with http4k is tempting if the domain model gets a little richer. Please classify the archetype, suggest a default stack, and give me repo-generation arguments.

### 15.

I want a research tool that compares several search backends for a local note corpus and measures retrieval quality for a fixed prompt set. This should stay experimental, reproducible, and Docker-backed. Please classify it and recommend whether to start as a local RAG system or a multi-storage experiment.

### 16.

I want a service that helps teams export data from a legacy API into cleaner structured bundles for downstream migrations. Go with Echo, Clojure with Kit, or Python FastAPI could all work depending on the shape you infer. Please plan the project first and produce a minimal repo command.

### 17.

I want a CLI that helps operators diff Dokku app configs across staging and production and flags dangerous mismatches. It should probably stay a CLI unless a small report view becomes necessary later. Please classify it, recommend the starting archetype and stack, and keep the generated repo tight.

### 18.

I want a small education tool that generates quiz sets from lecture transcripts and exposes a review API for a front-end that may come later. Python seems likely because of transcript processing, but I want the assistant to classify the repo before assuming service boundaries. Please recommend the best repo profile and `new_repo.py` args.

### 19.

I want to build a compact service that tracks document processing jobs, stores status transitions, and emits a simple operator-friendly progress API. Scala with Tapir and http4s could be a good fit, but I only want it if the added structure buys something real. Please classify and recommend the initial stack and workflow.

### 20.

I want a small internal automation tool that receives Slack slash-command requests and turns them into structured maintenance tasks. Deployment to Dokku is likely, and I care more about reliable smoke tests than about fancy architecture. Please classify the repo and generate a sensible starting command.

### 21.

I want a local-first finance tool that ingests bank CSV exports, normalizes merchant names, and produces monthly spending summaries. It feels like a data pipeline, but I might want a minimal API surface later for integrations. Please classify the archetype conservatively and recommend the smallest starting repo.

### 22.

I want a service that exposes a narrow API for querying experiment results from a DuckDB-backed analytics store. FastAPI plus Polars sounds natural, but I am open to Rust Axum if the shape really looks more service-heavy than data-heavy. Please classify and produce `new_repo.py` arguments.

### 23.

I want an internal observability tool that maps service owners to missing dashboards, missing smoke tests, and stale runbooks. Phoenix might be pleasant if a web surface matters, but a plain API could be enough at first. Please plan the repo shape and recommend the best initial stack.

### 24.

I want a workflow automation tool that turns recurring spreadsheet exports into cleaned JSON bundles and pushes them to downstream systems. Nim with Jester and HappyX sounds interesting if there is a light service wrapper, but this may just be a pipeline repo. Please classify it before picking a stack.

### 25.

I want a small SaaS idea for consultants who need to collect client documents, extract key deadlines, and generate a task timeline. Python seems likely, and Dokku deployment is probably enough for the first release. Please classify the project, recommend the starting stack, and give me the generation command.

### 26.

I want a developer dashboard that shows which repos still rely on copy-pasted examples instead of verified local patterns. The first version could be a simple API plus a few HTML fragments rather than a full front-end. Please classify the archetype and suggest whether Go Echo, Phoenix, or Dart Frog is the better fit.

### 27.

I want a local AI assistant tool that reads my project docs, summarizes current architecture, and proposes next implementation steps with citations. I care about deterministic indexing and clean handoff behavior more than flashy chat UI. Please classify it and recommend the smallest repo profile.

### 28.

I want an API platform experiment that exposes the same simple reporting surface in several languages so I can compare ergonomics and verification cost. This sounds like a polyglot lab to me, but I want the assistant to confirm that instead of assuming a normal backend service. Please plan the repo shape and generator args.

### 29.

I want a backend that helps a hiring team tag inbound resumes, surface duplicate candidates, and export structured review packets. Python FastAPI and Clojure Kit both seem viable depending on how much template rendering you think matters. Please classify and recommend the initial stack and context subset.

### 30.

I want a personal tool that tracks which books, essays, and talks I want to revisit and generates themed reading queues. It might start as a CLI, but I could imagine a tiny local web view later. Please keep the planning grounded and tell me which archetype to start with.

### 31.

I want a service that receives data export requests, tracks progress, and gives users a signed link when the export is ready. Go Echo, Kotlin http4k, or FastAPI all seem plausible, and Dokku deployment is likely. Please classify it, pick a primary stack, and output `new_repo.py` arguments.

### 32.

I want a document processing experiment that compares OCR post-processing strategies and stores intermediate results for later inspection. This feels like a multi-storage or pipeline repo rather than a normal service, but I want help choosing the right shape. Please classify and suggest the bounded repo profile.

### 33.

I want a compact internal tool that helps teams audit which prompts produced which generated artifacts during a project. A prompt-first repo might actually be the product here rather than just the planning environment. Please classify the idea and recommend the right generated repo setup.

### 34.

I want a small backend for collecting and querying structured field observations from a mobile workflow team. Rust Axum or Elixir Phoenix both sound interesting, but I want the assistant to recommend based on repo shape and likely verification burden. Please plan it first and keep the starting repo minimal.

### 35.

I want a CLI that generates starter repos for recurring internal service patterns and prints the reasoning behind the chosen profile. It may eventually call into this architecture, so I care about keeping the distinction between planning and generation clear. Please classify the archetype and suggest the best initial stack.

### 36.

I want a local education tool that ingests lecture notes, indexes them, and lets students ask focused questions with grounded answers. I want a Docker-backed workflow and deterministic small-corpus testing from the beginning. Please classify it and provide the correct `new_repo.py` plan.

### 37.

I want a backend service that monitors partner API freshness and warns when expected feeds have not updated on schedule. Python FastAPI, Go Echo, or Scala Tapir could all work depending on how much typed workflow structure you think is useful. Please classify the repo and recommend the initial stack.

### 38.

I want to build a small workflow automation service that turns emailed CSV attachments into normalized records and publishes an audit trail. Deployment to Dokku is likely, and I care about a clean smoke-test story. Please classify the project, recommend a stack, and generate the repo command.

### 39.

I want a developer-facing tool that compares two versions of an API surface and explains the likely migration impact in plain language. It might be a CLI or a tiny backend depending on how you classify the problem. Please do the planning first and keep the suggested repo profile tight.

### 40.

I want a small observability service that stores deployment events, release notes, and smoke-check outcomes so teams can see rollout history in one place. Clojure Kit, FastAPI, or Phoenix could all make sense depending on whether you optimize for simplicity or operator-facing views. Please classify and recommend the starting repo.

### 41.

I want a compact job search tool that scores open roles against my saved preferences and highlights why a role looks promising or weak. A local-only service is fine, and I want the first version to stay bounded and testable. Please classify the archetype, recommend a stack, and output generator arguments.

### 42.

I want a data export explorer where operators can preview the schema and sample rows of generated exports before sending them downstream. Go Echo or Dart Frog might both work if the UI stays light. Please classify the repo shape and recommend the smallest viable starting stack.

### 43.

I want an internal service that records prompt runs, extracted facts, validation outcomes, and handoff checkpoints for long research sessions. It needs continuity features from the start, but I do not want to overbuild the first repo. Please classify the idea and propose the right repo profile.

### 44.

I want a small finance operations tool that reconciles payouts from several processors and flags suspicious mismatches for manual review. Python FastAPI with Polars feels likely, but a pipeline shape might be more honest if the workflow is mostly batch. Please classify it and give me the `new_repo.py` command.

### 45.

I want a compact API that exposes curriculum metadata, reading assignments, and quiz availability for a small education product. Kotlin http4k or Rust Axum both sound plausible, and I want good Docker-backed verification. Please classify the project and recommend the initial profile.

### 46.

I want a local research assistant repo that tracks experiments, stores notes, and generates numbered follow-up prompts for future sessions. This may need prompt-first structure more than a conventional service surface. Please classify the repo, recommend the archetype and stack, and produce generation arguments.

### 47.

I want a service that helps internal platform teams see which repos are ready for Dokku deployment and which are missing the release path or smoke verification. It should stay straightforward and deployment-oriented. Please classify it and recommend whether Go Echo, FastAPI, or Phoenix is the better starting point.

### 48.

I want a multi-language experiment that implements the same tiny endpoint and smoke path in several ecosystems so I can compare assistant productivity and verification cost. I do not want the system to force a single-framework answer if the archetype is really comparative. Please classify it and suggest the correct repo shape.

### 49.

I want a document intake service for a small legal operations team that extracts deadlines, named parties, and status markers from uploaded files. Python seems likely, and Dokku deployment is enough, but I want the assistant to decide whether this starts as a service or a pipeline. Please classify and generate the repo arguments.

### 50.

I want a tiny internal tool that turns ad hoc team requests into a structured queue with owners, due dates, and completion notes, then exposes a minimal API and operator view. Elixir Phoenix, Go Echo, or Dart Frog could all work depending on how much UI you think belongs in the first slice. Please classify the project, recommend the best initial stack, and produce the smallest sensible `new_repo.py` command.
