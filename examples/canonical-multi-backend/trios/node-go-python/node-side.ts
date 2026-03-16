// Seam example: Node GraphQL BFF — Apollo Server 4 calling Go domain service over REST
// Seam 1 of 2: Node → Go via REST (GraphQL resolver calls GET /users/:id/recommendations)
// Not a full application. See context/stacks/trio-node-go-python.md.
//
// Architecture: [Node BFF] ── REST ──► [Go Services] ── REST ──► [Python ML]
// Node owns the GraphQL schema and client contract. Go owns domain data and
// calls Python ML internally. Node sees one Go endpoint; Python is invisible to Node.
//
// Dependencies:
//   @apollo/server   ^4.0  (Apollo Server 4, standalone mode)
//   graphql          ^16.0
//   tsx              ^4.0  (TypeScript execution)
//
// Environment:
//   GO_SERVICE_URL  — HTTP address of Go domain service (default: http://go-service:8080)
//   PORT            — Apollo Server GraphQL port (default: 3000)
//   HEALTH_PORT     — HTTP /healthz sidecar port (default: 3001)
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
  }

  type Recommendation {
    userId: ID!
    score: Float!
    category: String!
    reason: String!
  }

  type UserWithRecommendations {
    user: User!
    recommendations: [Recommendation!]!
  }

  type Query {
    """Fetch a user and their ML-scored recommendations. Go orchestrates the Go→Python call."""
    userWithRecommendations(userId: ID!): UserWithRecommendations
  }
`;

// ---------------------------------------------------------------------------
// Resolver — Seam 1: Node → Go REST call
// ---------------------------------------------------------------------------

interface GoUserRecommendations {
  user: { id: string; name: string; email: string };
  recommendations: Array<{ score: number; category: string; reason: string }>;
}

const resolvers = {
  Query: {
    // ── Seam interaction (1): call Go domain service over REST ──
    // Go handles the Go→Python ML call internally and returns a combined result.
    // Node's resolver is a single fetch; Go owns the downstream orchestration.
    userWithRecommendations: async (
      _: unknown,
      { userId }: { userId: string }
    ) => {
      const url = `${GO_SERVICE_URL}/users/${userId}/recommendations`;
      console.log(`[node-bff] calling Go: GET ${url}`);

      const res = await fetch(url, {
        signal: AbortSignal.timeout(5000),
      });

      if (!res.ok) {
        throw new Error(`go-service error: ${res.status} for userId=${userId}`);
      }

      const data = (await res.json()) as GoUserRecommendations;
      console.log(
        `[node-bff] received from Go: user=${data.user.id} recommendations=${data.recommendations.length}`
      );

      // Map Go's flat recommendation shape to the GraphQL type (add userId field)
      return {
        user: data.user,
        recommendations: data.recommendations.map((r) => ({
          userId,
          score: r.score,
          category: r.category,
          reason: r.reason,
        })),
      };
    },
  },
};

// ---------------------------------------------------------------------------
// Health probe — probes Go service; returns 200 or 503
// Downstream health probe pattern: this BFF is not healthy if Go is down.
// ---------------------------------------------------------------------------

async function probeGoService(): Promise<boolean> {
  try {
    const res = await fetch(`${GO_SERVICE_URL}/healthz`, {
      signal: AbortSignal.timeout(2000),
    });
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
      console.log(`[node-bff] HTTP /healthz listening on :${port}`);
    });
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  startHealthServer(HEALTH_PORT);

  const server = new ApolloServer({ typeDefs, resolvers });
  const { url } = await startStandaloneServer(server, {
    listen: { port: PORT },
  });

  console.log(`[node-bff] GraphQL endpoint: ${url}`);
  console.log(`[node-bff] GO_SERVICE_URL:   ${GO_SERVICE_URL}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
