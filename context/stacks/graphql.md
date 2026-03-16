# GraphQL

GraphQL is used in this repo primarily as the BFF (backend-for-frontend) layer in Node/TypeScript services that aggregate multiple downstream backends — Go domain services, Python ML services, or Elixir real-time systems — into a single typed API surface for frontend clients. It is not an internal service protocol in this repo; it is a client-facing aggregation layer.

## When GraphQL Is the Right Choice

- The BFF layer must serve multiple client types (mobile, web, third-party) with different field subsets — clients request exactly what they need, reducing over-fetching.
- Multiple underlying services (Go domain services, Python ML, Elixir real-time) need to be aggregated into a single typed API surface for the frontend without the frontend needing to know about each service individually.
- Subscriptions are needed for real-time updates — GraphQL subscriptions over WebSocket are the standard pattern for pushing events to subscribers without polling.
- The frontend team owns the GraphQL schema and drives API shape (schema-first) independently of the backend service teams.
- API introspection is a requirement — clients can self-discover the schema, enabling typed codegen for frontend frameworks.

## When GraphQL Is NOT the Right Choice

- Simple CRUD APIs with one client type — REST is simpler to implement and consume; GraphQL adds schema, resolver, and codegen overhead that is not justified.
- The caller is a non-frontend service calling another service — use REST or gRPC between backend services; GraphQL is a BFF pattern, not an internal service protocol.
- Real-time requires stateful bidirectional streams at high frequency (voice, game frames, binary telemetry) — WebSocket without GraphQL is more efficient for high-frequency binary streams where GraphQL's field selection adds unnecessary parsing overhead.
- The team is unfamiliar with GraphQL — the learning curve (resolvers, N+1, schema evolution, error handling semantics) adds delivery risk; start with REST and migrate to GraphQL once the BFF concern is real.

## Typical Repo Surface

Node/TypeScript BFF with Apollo Server (schema-first):

```
src/
  schema.graphql          — SDL schema definition (schema-first preferred)
  resolvers/              — resolver implementations per type (Query, Mutation, Subscription, Type)
  dataloaders/            — DataLoader instances for batching downstream calls
  generated/              — graphql-codegen output (types.ts, resolver signatures)
  context.ts              — Context type definition and per-request context factory
codegen.yml               — graphql-codegen configuration
```

Code-first alternative (Pothos):

```
src/
  schema.ts               — Pothos schema builder; types and fields defined in TypeScript
  resolvers/              — same structure; types are inferred from Pothos, not codegen
```

## Schema Design Principles

- **Schema-first preferred:** write the `.graphql` SDL file, generate TypeScript types for both server resolvers (graphql-codegen `typescript-resolvers`) and the client (gql.tada or graphql-codegen `client` preset). This keeps the schema human-readable and decouples server and client type generation.
- Use GraphQL enums for finite value sets — avoids stringly-typed fields that drift out of sync across services.
- Prefer nullable fields for optional data. The GraphQL null semantic means "this field may not exist" — overusing non-null (`!`) causes partial responses where a single missing field nullifies the entire object.
- Non-null (`!`) only on fields that are structurally guaranteed to exist — `id`, `createdAt`, required keys.
- Use Relay cursor-based pagination (`Connection` / `Edge` / `Node`) for paginated lists:
  ```graphql
  type UserConnection {
    edges: [UserEdge!]!
    pageInfo: PageInfo!
  }
  type UserEdge {
    cursor: String!
    node: User!
  }
  ```
- Return typed unions for operations that have multiple outcomes — do not return raw error strings in schema fields:
  ```graphql
  union CreateUserResult = User | UserAlreadyExistsError | ValidationError
  type Mutation {
    createUser(input: CreateUserInput!): CreateUserResult!
  }
  ```

## Query and Mutation Resolvers

Apollo Server 4, TypeScript, schema-first with graphql-codegen:

```typescript
// src/resolvers/User.ts
import { Resolvers } from '../generated/types';

export const userResolvers: Resolvers = {
  Query: {
    user: async (_, { id }, { goUsersUrl }) => {
      const resp = await fetch(`${goUsersUrl}/users/${id}`);
      if (!resp.ok) return null;
      return resp.json();
    },
    users: async (_, __, { goUsersUrl }) => {
      const resp = await fetch(`${goUsersUrl}/users`);
      return resp.json();
    },
  },
};
```

Context type — downstream service URLs and DataLoader instances are injected per request:

```typescript
// src/context.ts
import DataLoader from 'dataloader';

export interface Context {
  goUsersUrl: string;
  pythonScoringUrl: string;
  userLoader: DataLoader<string, User>;
}

export function buildContext({ req }: { req: Request }): Context {
  return {
    goUsersUrl: process.env.GO_USERS_URL ?? 'http://go-users:8080',
    pythonScoringUrl: process.env.PYTHON_SCORING_URL ?? 'http://python-scoring:8001',
    userLoader: createUserLoader(process.env.GO_USERS_URL ?? 'http://go-users:8080'),
  };
}
```

Resolvers should only call downstream services and transform responses. Business logic belongs in downstream APIs, not in resolvers.

## Subscriptions (WebSocket, Server-Sent Events)

Apollo Server 4 does not bundle a WebSocket server. Use `graphql-ws` + `ws`:

```typescript
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { useServer } from 'graphql-ws/lib/use/ws';
import { makeExecutableSchema } from '@graphql-tools/schema';

const schema = makeExecutableSchema({ typeDefs, resolvers });
const httpServer = createServer(app);
const wsServer = new WebSocketServer({ server: httpServer, path: '/graphql' });
useServer({ schema }, wsServer);
httpServer.listen(PORT);
```

Schema definition for subscriptions:

```graphql
type Subscription {
  stateUpdated(docId: ID!): StateUpdate!
}

type StateUpdate {
  docId: ID!
  eventType: String!
  data: JSON
}
```

Resolver — subscribe to a NATS subject and yield updates as an async generator:

```typescript
Subscription: {
  stateUpdated: {
    subscribe: async function* (_, { docId }, { natsConn }) {
      const sub = natsConn.subscribe(`state.${docId}.updates`);
      try {
        for await (const msg of sub) {
          const event = JSON.parse(msg.string());
          yield { stateUpdated: event };
        }
      } finally {
        sub.unsubscribe(); // clean up on client disconnect
      }
    },
  },
},
```

Clean up subscriptions on disconnect. Subscription connections are long-lived; leaking NATS subscriptions or database connections on client disconnect is a common mistake.

## DataLoader Pattern (N+1 Prevention)

Any resolver that loads child objects for a list will produce N+1 downstream calls without DataLoader. DataLoader batches multiple calls within a single tick into one downstream request.

```typescript
// src/dataloaders/userOrders.ts
import DataLoader from 'dataloader';
import { Order } from '../generated/types';

export const createUserOrdersLoader = (goOrdersUrl: string) =>
  new DataLoader<string, Order[]>(async (userIds) => {
    const resp = await fetch(`${goOrdersUrl}/orders/bulk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_ids: userIds }),
    });
    const orderMap: Record<string, Order[]> = await resp.json();
    // Must return results in the same order as userIds
    return userIds.map(id => orderMap[id] ?? []);
  });
```

Create DataLoader instances per request (in context factory), not as module-level singletons — DataLoaders are stateful and must not persist across requests.

## Code Generation

`graphql-code-generator` generates typed resolvers and TypeScript types from the `.graphql` schema.

`codegen.yml` — server types and resolver signatures:

```yaml
schema: src/schema.graphql
generates:
  src/generated/types.ts:
    plugins:
      - typescript
      - typescript-resolvers
    config:
      contextType: '../context#Context'
      useIndexSignature: true
```

`codegen.yml` — client preset (React, Next.js, typed hooks):

```yaml
schema: src/schema.graphql
documents: src/**/*.graphql
generates:
  src/generated/client/:
    preset: client
```

Run: `npx graphql-codegen --config codegen.yml`

Add to CI and to a pre-build step so generated types are never stale. Do not hand-write TypeScript types for GraphQL responses — they will drift from the schema.

## Federation (Apollo Federation v2)

Federation splits a large GraphQL schema across multiple subgraph services, each owned by a different team. The Apollo Router merges them into a supergraph at query time.

**When to use:**
- Multiple teams each own a segment of the GraphQL schema with independent deployment cycles.
- The schema has grown beyond what a single BFF can reasonably own and maintain.
- Different subgraphs need different scaling profiles.

**When NOT to use:**
- Single-team BFF calling 2–3 downstream services — a single Apollo Server is simpler and has no router overhead.
- The schema is stable and owned by one team.

Key directives:

```graphql
# In the Users subgraph
type User @key(fields: "id") {
  id: ID!
  name: String!
  email: String!
}

# In the Orders subgraph — extends User with orders
extend type User @key(fields: "id") {
  id: ID! @external
  orders: [Order!]!
}
```

Use `rover` CLI to compose the supergraph schema locally:

```bash
rover supergraph compose --config supergraph.yaml
```

## Language Coverage

### Node/TypeScript (primary in this repo)

**Runtime:** Apollo Server 4
**Schema approach:** schema-first (`.graphql` SDL) + graphql-codegen; or code-first with Pothos
**Subscriptions:** `graphql-ws` + `ws`
**DataLoader:** `dataloader` npm package
**Codegen:** `@graphql-codegen/cli` with `typescript` + `typescript-resolvers` plugins

Node is the GraphQL BFF in all multi-backend patterns in this repo (duo-node-go, duo-node-elixir, trio-node-go-python). It calls Go and Python downstreams over REST and aggregates results for the frontend.

### Go

**Runtime:** `gqlgen` (code-first, generates Go types from schema — no reflection at runtime)
**Use case in this repo:** Go as a standalone GraphQL server is uncommon — Go is typically a REST downstream called by the Node BFF. Use gqlgen only if Go owns the GraphQL surface directly (teams without a Node BFF layer).

```go
// gqlgen generates from schema.graphqls and gqlgen.yml
// Resolvers are in graph/resolver.go
```

### Python

**Options:** Strawberry (code-first, Pythonic decorator syntax) or Ariadne (schema-first, similar to Apollo Server)
**Use case in this repo:** Python ML service exposed via GraphQL is uncommon — prefer FastAPI REST for Python services. Use Strawberry if Python must own a GraphQL surface.

```python
# Strawberry example
import strawberry

@strawberry.type
class Query:
    @strawberry.field
    def predict(self, features: list[float]) -> str:
        return "positive"

schema = strawberry.Schema(query=Query)
```

### Elixir

**Runtime:** Absinthe (schema-first, functional resolvers, Phoenix integration, built-in subscription support via Phoenix PubSub)
**Use case in this repo:** Elixir may expose a standalone Absinthe GraphQL API for real-time features as an alternative to the Node BFF pattern. Absinthe subscriptions integrate directly with Phoenix PubSub and Phoenix Channels — Elixir handles the subscription lifecycle natively without `graphql-ws`.

```elixir
# Absinthe schema definition
defmodule MyApp.Schema do
  use Absinthe.Schema

  subscription do
    field :state_updated, :state_update do
      arg :doc_id, non_null(:id)
      config fn args, _ ->
        {:ok, topic: args.doc_id}
      end
    end
  end
end
```

In this repo's patterns:
- Node is the GraphQL BFF (Apollo Server) that calls Go REST and Python REST downstreams.
- Elixir may expose a standalone Absinthe GraphQL API for real-time features as a separate surface (see `context/stacks/duo-node-elixir.md`).
- Go, Python, and Elixir as GraphQL servers are secondary patterns used when a team does not use a Node BFF.

## Local Dev Composition

Node BFF calling a Go domain service:

```yaml
services:
  go-service:
    build: ./services/domain
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3

  node-bff:
    build: ./services/bff
    ports:
      - "3000:3000"
    environment:
      GO_SERVICE_URL: http://go-service:8080
      PORT: "3000"
    depends_on:
      go-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s
```

The Node BFF health endpoint should probe each downstream service and return degraded status if any are unreachable.

## Testing Expectations

- **Schema validation:** ensure schema compiles with `makeExecutableSchema` in a unit test — catch SDL errors before runtime.
- **Resolver unit tests:** mock the downstream HTTP calls (not the entire downstream service) using `jest.spyOn(global, 'fetch')` or a test `Context`; assert the resolver returns the correct shape.
- **Integration test:** `docker compose up go-service node-bff`; send a real GraphQL query to `http://localhost:3000/graphql`; assert the response shape end-to-end.
- **Subscription test:** use a WebSocket client (`graphql-ws` client) in tests; publish an event to NATS or trigger a state change; assert the subscription yields the expected message within a timeout.
- **DataLoader test:** verify the batch function is called once for multiple resolver calls in a single request (not once per resolver call).
- Do NOT mock the GraphQL layer itself — test at the HTTP/WebSocket boundary to catch integration failures.

## Common Assistant Mistakes

- **Business logic in resolvers.** Resolvers should only call downstream services and transform responses for the client. Domain rules belong in downstream APIs, not in the BFF resolver layer.
- **Missing DataLoader for nested list fields.** Any resolver that loads a child object for each item in a parent list produces N+1 downstream calls without DataLoader. Every nested list is a DataLoader candidate.
- **Leaking subscription resources.** Subscription connections are long-lived. Always clean up NATS subscriptions, database cursors, or event emitter listeners in the `finally` block of the async generator.
- **Confusing HTTP 200 with GraphQL success.** GraphQL always returns HTTP 200, even on errors. Errors appear in the `errors` field of the response body. Do not check `resp.ok` to determine if a GraphQL query succeeded.
- **Using mutations for reads.** Queries are idempotent and cacheable; mutations are not. Use the correct operation type.
- **Hand-writing TypeScript types for GraphQL responses.** Always generate types from the schema using graphql-codegen. Hand-written types drift from the schema and break silently.
- **Over-using federation.** A single Apollo Server calling 2–3 downstream services does not need federation. Add federation only when multiple teams own separate schema segments with independent deployment cycles.

## Related

- `context/stacks/typescript-hono-bun.md` — Node/TypeScript stack
- `context/stacks/duo-node-go.md` — GraphQL BFF + Go domain services pattern
- `context/stacks/duo-node-elixir.md` — GraphQL subscriptions + Elixir distributed state
- `context/stacks/trio-node-go-python.md` — Node GraphQL BFF in a three-service system
- `context/stacks/elixir-phoenix.md` — Absinthe for Elixir-native GraphQL
- `examples/canonical-multi-backend/duos/node-go-rest/` — canonical Node + Go seam example with GraphQL BFF
