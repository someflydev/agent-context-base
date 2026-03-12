# Deployment Philosophy: Dokku

Dokku is a first-class deployment target for many future service repos derived from this base.

## Why Dokku Fits This Base

- simple operational model
- good match for single-service repos
- works well with explicit Dockerfiles or buildpacks
- keeps deployment guidance practical instead of platform-specific sprawl

## Default Assumptions

- each deployable repo should ship as its own service repo
- deployment config should stay close to the service
- backing services should be provisioned explicitly
- release commands and migrations should be deliberate, not implicit magic

## Repo Design Implications

- keep service boundaries clear
- prefer environment-driven configuration
- keep container boot paths explicit
- design smoke tests that can prove the deployed service booted correctly

## Dokku And Testing

Dokku guidance does not remove the need for local Docker-backed dev and test stacks. Local verification should happen before deployment wiring is trusted.

## Anti-Patterns

- turning the base repo into a Dokku-specific platform product
- assuming every future repo deploys the same way
- hiding migrations, seeds, or build steps behind unclear deploy hooks

