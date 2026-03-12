# Add Deployment Support

Use this workflow when a repo needs explicit deployment guidance or wiring, especially for Dokku.

## Preconditions

- the service entrypoint is known
- environment and backing-service needs are known

## Sequence

1. confirm the repo is actually deployable as a single service
2. load `context/doctrine/deployment-philosophy-dokku.md`
3. add the minimal deploy artifacts needed by the stack
4. document required environment variables and backing services
5. add or update smoke tests that can prove post-deploy boot success
6. add minimal real-infra integration tests locally for any significant storage or search dependency before trusting deploy wiring

## Outputs

- deploy guidance or deploy files
- boot verification path
- environment contract documentation

## Related Docs

- `context/stacks/dokku-conventions.md`
- `context/archetypes/dokku-deployable-service.md`

## Common Pitfalls

- hiding important release steps
- assuming deployment success proves persistence wiring
- mixing multi-service platform design into a single-service repo

