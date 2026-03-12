# Stop Conditions

Stop and clarify when:

- repo profile and repo contents disagree
- more than one archetype seems primary and no composition rule exists
- more than one stack seems primary for the touched files
- no preferred example exists for a sensitive change
- the task touches persistence, queues, or search but no integration-test path exists
- Docker-backed changes would break dev/test isolation
- a requested stack has no stack pack and no local canonical example

Do not continue by inventing conventions silently.
