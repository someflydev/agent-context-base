// This is a seam-focused example.
// For a full application scaffold, see context/archetypes/multi-backend-service.md.
//
// node-side.ts — Node/TypeScript GraphQL BFF (Apollo Server 4, standalone mode).
// Resolves GraphQL queries by calling the Go domain service over HTTP/REST.
// Also exposes a minimal HTTP /healthz endpoint (on HEALTH_PORT) that probes Go.
//
// This example lightly previews the GraphQL BFF pattern before a dedicated
// graphql.md stack doc is added in PROMPT_60.
//
// Dependencies:
//   @apollo/server   ^4.0
//   graphql          ^16.0
//   tsx              ^4.0  (TypeScript execution — used by docker-compose CMD)
//
// Environment:
//   GO_SERVICE_URL  — HTTP address of the Go domain service (default: http://go-service:8080)
//   PORT            — Port for the GraphQL endpoint (default: 3000)
//   HEALTH_PORT     — Port for the /healthz endpoint (default: 3001)
//
// GraphQL runs on PORT; /healthz runs on HEALTH_PORT.
// docker-compose healthcheck targets HEALTH_PORT.

import { ApolloServer } from "@apollo/server";
import { startStandaloneServer } from "@apollo/server/standalone";
import * as http from "http";

const GO_SERVICE_URL = process.env.GO_SERVICE_URL ?? "http://go-service:8080";
const PORT = parseInt(process.env.PORT ?? "3000", 10);
const HEALTH_PORT = parseInt(process.env.HEALTH_PORT ?? "3001", 10);

// ---------------------------------------------------------------------------
// GraphQL schema
// ---------------------------------------------------------------------------

const typeDefs = `#graphql
  type User {
    id: ID!
    name: String!
    email: String!
    createdAt: String!
  }

  type Query {
    """Fetch a single user by ID. Returns null if not found."""
    user(id: ID!): User

    """Fetch all users."""
    users: [User!]!
  }
`;

// ---------------------------------------------------------------------------
// Resolvers — call Go REST service via fetch (Node 18+ built-in)
// ---------------------------------------------------------------------------

interface GoUser {
  id: string;
  name: string;
  email: string;
  created_at: string;
}

function mapUser(u: GoUser) {
  return {
    id: u.id,
    name: u.name,
    email: u.email,
    createdAt: u.created_at,
  };
}

const resolvers = {
  Query: {
    user: async (_: unknown, { id }: { id: string }) => {
      const res = await fetch(`${GO_SERVICE_URL}/users/${id}`);
      if (res.status === 404) return null;
      if (!res.ok) throw new Error(`go-service error: ${res.status}`);
      return mapUser((await res.json()) as GoUser);
    },

    users: async () => {
      const res = await fetch(`${GO_SERVICE_URL}/users`);
      if (!res.ok) throw new Error(`go-service error: ${res.status}`);
      return ((await res.json()) as GoUser[]).map(mapUser);
    },
  },
};

// ---------------------------------------------------------------------------
// Health probe — probes Go service; returns 200 or 503
// Downstream health probe pattern: this service is not healthy if Go is down.
// ---------------------------------------------------------------------------

async function probeGoService(): Promise<boolean> {
  try {
    const res = await fetch(`${GO_SERVICE_URL}/healthz`, { signal: AbortSignal.timeout(2000) });
    return res.ok;
  } catch {
    return false;
  }
}

function startHealthServer(port: number): void {
  http
    .createServer(async (req, res) => {
      if (req.url !== "/healthz") {
        res.writeHead(404).end("not found");
        return;
      }
      const goOk = await probeGoService();
      if (goOk) {
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ status: "ok" }));
      } else {
        res.writeHead(503, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ status: "degraded", reason: "go-service unreachable" }));
      }
    })
    .listen(port, () => {
      console.log(`HTTP /healthz listening on :${port}`);
    });
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  // Start the /healthz probe server on HEALTH_PORT.
  startHealthServer(HEALTH_PORT);

  // Start Apollo Server (standalone) on PORT for GraphQL.
  const server = new ApolloServer({ typeDefs, resolvers });
  const { url } = await startStandaloneServer(server, {
    listen: { port: PORT },
  });

  console.log(`GraphQL endpoint: ${url}`);
  console.log(`GO_SERVICE_URL:   ${GO_SERVICE_URL}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
