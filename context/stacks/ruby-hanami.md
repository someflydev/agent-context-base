# Ruby: Hanami

Use this pack for Ruby backend services that want Hanami 2 style routing, action classes, and view rendering with small explicit service boundaries.

## Compatible Archetypes

- `backend-api-service`
- `interactive-data-service`

## Typical Repo Surface

- `Gemfile`
- `config.ru`
- `app/router.rb`
- `app/actions/**/*.rb`
- `app/views/**/*.rb`
- `app/` ERB fragment templates
- `lib/**/*.rb`
- `spec/`

## Common Change Surfaces

- Hanami router declarations and route-to-action wiring
- action classes that shape JSON and HTML fragment responses
- `Hanami::View` classes and ERB templates for HTMX-style partials
- Sequel repositories or query helpers that feed API and chart payloads
- Dockerfiles used for smoke verification when host Ruby tooling is absent

## Testing Expectations

- Docker-backed smoke test for boot plus one health route
- one representative JSON API route that exercises a small Sequel query helper
- one HTML fragment surface check when the service feeds HTMX-style clients
- one chart-data payload check for dashboard or Plotly-oriented consumers

## Common Assistant Mistakes

- collapsing Hanami routing, action, and view concerns into one large Rack file
- returning hand-built HTML strings when a small `Hanami::View` template should define the fragment contract
- hiding Sequel dataset shaping inside transport code instead of a named persistence helper
