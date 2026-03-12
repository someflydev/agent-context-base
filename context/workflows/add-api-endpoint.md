# Add API Endpoint

Purpose: add a route or handler in a backend service.

Sequence:

1. confirm active backend stack
2. inspect the preferred endpoint example for that stack
3. add route, handler, service, and test in the local preferred shape
4. add smoke coverage for the happy path
5. add real integration coverage if storage, queues, or search are touched

Pitfalls:

- business logic inside route files
- skipping smoke coverage
