# Single-Service Bias

Prefer a single deployable service when it fits the problem.

Choose more services only when the boundary is operationally meaningful, not because the architecture looks cleaner in theory.

Apply this doctrine when:

- introducing queues, workers, or secondary services
- splitting an API from a simple UI
- deciding whether Dokku packaging should stay single-app

Common mistakes prevented:

- premature service decomposition
- introducing orchestration needs before they are justified
- turning local experiments into needlessly distributed systems
