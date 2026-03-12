# Agent Context Base Architecture Mental Model

The current repository behaves like a context operating system for future repos, not like an application. Its own analyzer resolves it as a `prompt-first-repo` with the `prompt-first-meta-repo` manifest, and the full integrity check currently passes across 14 manifests. The architecture is therefore best understood as a deterministic narrowing pipeline: infer intent, detect repo shape, assemble the smallest valid bundle, implement, then validate.

## SECTION 1 - System Overview Diagram

```mermaid
flowchart LR
    U[User] -->|task request| A[Assistant]

    A -->|entrypoint read| E[README + repo-purpose + repo-layout + session-start]
    A -->|inspect repo signals| P[Project Repo]

    subgraph CS[Context System]
        R[Router Layer<br/>task router<br/>stack router<br/>archetype router<br/>alias catalog<br/>repo-signal hints]
        M[Manifest Layer<br/>bundle definitions]
        D[Doctrine Layer]
        W[Workflow Layer]
        S[Stack Layer]
        AR[Archetype Layer]
        EX[Examples Layer]
        T[Templates Layer]
        SC[Scripts Layer<br/>validate<br/>preview<br/>bootstrap<br/>analyze<br/>diff]
    end

    E --> R
    P -->|files, lockfiles, tests,<br/>Compose, Procfile, prompts| R
    R --> M
    M --> D
    M --> W
    M --> S
    M --> AR
    M --> EX
    M -. scaffolding only .-> T

    SC --> R
    SC --> M
    SC --> EX

    D --> A
    W --> A
    S --> A
    AR --> A
    EX --> A
    T -. optional .-> A
    SC --> A

    A -->|implementation, validation, refinement| P
```

This is the real control shape of the repo. The assistant does not start from "scan everything"; it starts from a small entrypoint, uses routers to infer the active task and repo shape, lets manifests assemble a bounded context set, then uses examples to shape implementation. The "Project Repo" is usually a descendant repo, but for meta-work inside this repository it can be this repo itself.

## SECTION 2 - Context Layer Stack Diagram

```mermaid
flowchart TB
    H[Human Task Intent]
    R[Router Layer]
    M[Manifest Layer]
    D[Doctrine]
    W[Workflows]
    S[Stacks]
    A[Archetypes]
    E[Examples]
    G[Generated Implementation]

    H --> R --> M
    M --> D
    M --> W
    M --> S
    M --> A
    D --> E
    W --> E
    S --> E
    A --> E
    E --> G
```

Information flows downward by increasing specificity. Human intent is ambiguous; routers turn it into a probable task, stack, and archetype; manifests convert that inference into explicit file lists; doctrine constrains behavior; workflows sequence work; stacks and archetypes localize technical detail; examples finally shape the output surface.

Stable layers are doctrine, routers, example metadata, weights, templates, and the pack documents themselves. Task-specific choices are the selected workflow, selected archetype, active stack set, chosen manifest, and chosen canonical example.

## SECTION 3 - Router Inference Flow Diagram

```mermaid
flowchart TB
    U[User Task Description] --> I{Task intent clear?}
    I -->|yes| T[Task router<br/>+ task inference skill]
    I -->|no| STOP1[Stop condition:<br/>do not expand blindly]

    T --> RS[Inspect repo signals<br/>lockfiles, source paths,<br/>tests, Compose, Procfile, prompts]
    RS --> AL[Apply aliases<br/>and natural-language mappings]
    AL --> ST{Dominant stack?}
    ST -->|no| STOP2[Pause on stack ambiguity]
    ST -->|yes| AR{Primary archetype?}
    AR -->|no| STOP3[Pause on repo-shape ambiguity]
    AR -->|yes| MM[Match manifests by<br/>triggers, aliases, repo_signals]
    MM --> MF{Close manifest match?}
    MF -->|yes| CB[Assemble context bundle]
    MF -->|no| SM[Fallback to smallest manual bundle]
    CB --> CE[Rank canonical examples]
    SM --> CE
    CE --> IR[Implementation reasoning]
```

This is exactly what the repository encodes in the task router, stack router, archetype router, alias catalog, repo-signal hints, and stop-condition doctrine. The prompt analyzer operationalizes the repo-signal step, while the alias catalog makes normal language usable without requiring users to know internal filenames.

The key design choice is that ambiguity stops expansion rather than triggering more loading. That is how the repo prevents "I'm not sure, so I'll read everything."

## SECTION 4 - Manifest-Driven Context Assembly Diagram

```mermaid
flowchart TB
    M[Manifest]
    M --> TW[triggers + aliases + task_hints]
    M --> RS[repo_signals]
    M --> RC[required_context]
    M --> OC[optional_context]
    M --> PE[preferred_examples]
    M --> RT[recommended_templates]
    M --> OP[bootstrap_defaults<br/>Compose names<br/>port bands<br/>data isolation<br/>Dokku relevance]

    TW --> R[Router selection]
    RS --> R

    RC --> B[Ordered context bundle]
    OC --> B
    PE --> B

    B --> A[Assistant reasoning]
    RT -. scaffold only if needed .-> A
    OP --> O[Bootstrap and operational behavior]
```

Manifests are the repo's context glue because they bind inference to concrete files. They do three jobs at once: help routers decide whether a manifest fits, declare the exact context to load, and carry operational defaults such as Compose naming, port bands, data isolation, smoke expectations, and Dokku support.

The actual bundle order is deterministic: repository entrypoints first, then the manifest itself, then required context, then optional context, then preferred examples. Metadata is distributed but coherent: alias metadata lives in the alias catalog, example metadata in the example catalog, context weighting in the weights file, and manifest schema rules in code rather than in a separate schema file.

## SECTION 5 - Canonical Example Influence Diagram

```mermaid
flowchart LR
    B[Context Bundle] --> X[Example ranking metadata]
    X --> P[Pick one preferred canonical example]
    P --> R[Assistant reasoning]
    R --> C[Generated code / docs / tests]

    D[Doctrine] --> R
    T[Template scaffold] -. lower authority .-> C
```

Examples exist late in the pipeline on purpose. They are not discovery tools; they are implementation-shaping tools once the task, stack, and archetype are already narrow.

This prevents hallucinated architecture in three ways. First, ranking is explicit rather than memory-based. Second, one preferred example is favored over blended hybrids. Third, templates stay lower-authority than canonical examples, so scaffolds do not become accidental architecture.

## SECTION 6 - Assistant Execution Loop Diagram

```mermaid
flowchart TB
    TI[Task interpretation]
    CL[Context loading]
    EC[Example consultation]
    IA[Implementation attempt]
    VA[Validation]
    ST[Smoke / integration verification]
    RF[Refinement]
    DN[Ready change]

    TI --> CL --> EC --> IA --> VA --> ST
    ST -->|fails or ambiguity remains| RF
    RF --> CL
    ST -->|passes| DN

    DO[Doctrine] --> CL
    DO --> RF
    WF[Workflow] --> TI
    WF --> IA
```

Doctrine and workflows play different roles in the loop. Doctrine says what must remain true: minimal context, canonical-example priority, test realism, Compose isolation, prompt monotonicity, stop conditions. Workflows say what order to do work in: identify surface, implement happy path, add smoke coverage, add real boundary verification if needed, refine.

This makes the loop conservative without making it static. The assistant can iterate, but every iteration is still routed and constrained.

## SECTION 7 - Context Integrity and Validation Diagram

```mermaid
flowchart TB
    CH[Changes to manifests / examples / templates / routers / scripts]
    CH --> VC[validate_context.py]

    VC --> VM[Manifest validation]
    VC --> CW[Context weight checks]
    VC --> EC[Example catalog checks]
    VC --> RH[Repo-signal hint checks]
    VC --> PN[Prompt numbering checks]
    VC --> BI[Bootstrap invariant checks<br/>generated temp repos]

    PB[preview_context_bundle.py] --> INS1[Inspect load order,<br/>weights, anchors, ranked examples]
    PA[prompt_first_repo_analyzer.py] --> INS2[Infer stacks, archetypes,<br/>workflows, manifests from repo signals]
    PD[pattern_diff.py] --> INS3[Compare candidate vs<br/>canonical pattern or template]
```

This layer is why the system stays healthy over time instead of decaying into inconsistent docs. Validation does not just lint syntax; it checks that manifests point to real files, that example metadata covers the real example set, that prompt numbering stays monotonic, and that bootstrapped repos preserve Compose names, isolated ports, distinct env files, and separate dev/test volume roots.

A subtle but important detail is that the manifest schema is enforced in code. That keeps the schema executable, not merely documented.

## SECTION 8 - Deployment and Operational Layer Diagram

```mermaid
flowchart LR
    AR[Archetypes<br/>backend-api-service<br/>dokku-deployable-service] --> M[Manifests]
    ST[Stack packs<br/>service stack + dokku conventions] --> M
    DO[Deployment doctrine<br/>testing doctrine<br/>Compose isolation doctrine] --> M

    M --> BR[Bootstrap / render]
    BR --> CP[Compose topology<br/><repo> and <repo>-test<br/>non-overlapping ports<br/>isolated volumes]
    BR --> DK[Dokku artifacts<br/>Procfile, app.json,<br/>deployment docs]
    CP --> LV[Local verification]
    DK --> LV
    LV --> SM[Smoke tests]
    LV --> IT[Minimal real-infra integration tests]
    SM --> DR[Deployment readiness]
    IT --> DR
```

Deployment is not a separate universe in this architecture. It is an extension of the same routing model: archetype says "single deployable service," stack says "what boots," doctrine says "what must be explicit," manifests carry the operational defaults, and smoke plus integration tests prove the service locally before Dokku wiring is trusted.

The philosophy is intentionally narrow: simple deployable services, explicit release surfaces, and local isolation first. This repo is not trying to grow into a platform orchestration framework.

## SECTION 9 - Failure Modes Diagram

```mermaid
flowchart TB
    F1[Load too much context] --> G1[Context-loading rules<br/>session-start discipline<br/>weight metadata]
    F2[Blend incompatible examples] --> G2[Canonical-example doctrine<br/>example ranking<br/>one-example preference]
    F3[Infer stack from weak signal] --> G3[Stack/archetype routers<br/>repo-signal hints<br/>repo analyzer]
    F4[Invent unsupported structure] --> G4[Stack packs<br/>extension-path guidance<br/>stop conditions]
    F5[Change storage/deploy behavior<br/>without proof] --> G5[Testing doctrine<br/>workflow checks<br/>smoke + real boundary tests]
    F6[Cross-contaminate dev/test infra] --> G6[Compose isolation doctrine<br/>manifest port/data metadata<br/>bootstrap validation]
    F7[Prompt or naming drift] --> G7[Prompt-first doctrine<br/>post-flight refinement<br/>prompt numbering validation]
    F8[Overengineering] --> G8[Core principles:<br/>build the smallest useful thing]
```

This is the repository's real anti-hallucination model. It does not assume assistants will "be careful"; it builds explicit structural countermeasures against the common ways assistants go wrong.

The most important defense is not any single rule. It is the combination of bounded loading, manifest assembly, ranked canonical examples, and hard stop conditions when ambiguity persists.

## SECTION 10 - Evolution Diagram

```mermaid
flowchart LR
    N[New recurring need] --> C1[Add focused stack / workflow / archetype doc]
    C1 --> C2[Add aliases and repo-signal hints]
    C2 --> C3{Is it first-class now?}
    C3 -->|yes| C4[Add or update manifest]
    C3 -->|no| C5[Keep as extension path]

    C4 --> C6{Is there a stable canonical pattern?}
    C6 -->|yes| C7[Add canonical example + catalog metadata]
    C6 -->|no| C8[Do not add example yet]

    C4 --> C9{Need scaffolding?}
    C9 -->|yes| C10[Add template + bootstrap support]
    C9 -->|no| C11[No scaffold]

    C7 --> V[Update validation and analyzer rules]
    C10 --> V
    C2 --> V
    V --> L[Record structural change in evolution docs]
```

The growth model is staged and deliberately asymmetric. New stacks can begin as extension paths; they do not become manifest-backed, example-backed, or template-backed until the pattern is recurring and stable.

That is what allows safe growth. The repo can expand its coverage without turning every idea into first-class architecture.

## SECTION 11 - Visual Mental Model Summary

"Routers infer intent, manifests assemble context, doctrine constrains behavior, workflows sequence execution, stacks and archetypes localize detail, and canonical examples keep implementation from drifting."

In practice, this means the repository behaves less like documentation and more like a deterministic control plane for assistant reasoning. The assistant reads a small entrypoint, infers the task and repo shape, loads one bounded bundle, uses one canonical example to shape output, validates the result, and stops when ambiguity would otherwise force invention.
