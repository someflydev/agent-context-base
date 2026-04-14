# PHP Canonical Faker Example

What this demonstrates: FakerPHP (imperative) vs. Alice (declarative)

The core contrast: imperative full control vs. readable-but-limited YAML

- Alice's strengths: team-readable, expressive cross-references, quick setup
- Alice's limitations: no weighted distributions natively, no temporal rules, not suited for large volumes
- When to use each approach

Quick start: `composer install && php generate.php --profile smoke`

How to test: `./vendor/bin/phpunit tests/`

How to validate: `python3 ../../domain/validate_output.py --input-dir ./output/smoke`
