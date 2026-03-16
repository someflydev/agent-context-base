// This is a seam-focused example.
// For a full application scaffold, see context/archetypes/multi-backend-service.md.
//
// node-side.ts — Node/TypeScript NATS publisher + subscriber (bidirectional).
//
// Node owns the client connection layer. This side:
//   1. Connects to NATS (core NATS — no JetStream).
//   2. Subscribes to "state.*.updates" to receive state broadcasts from Elixir.
//   3. Publishes one demo client action to "actions.sess-demo.cursor.moved".
//   4. Exposes GET /healthz via Hono.
//
// This is BIDIRECTIONAL: Node both publishes (client actions) and subscribes
// (state updates from Elixir). Contrast with go-elixir-nats which is unidirectional.
//
// npm dependencies:
//   nats@2         -- NATS.js v2 client (core NATS + JetStream)
//   hono           -- lightweight HTTP framework (matches typescript-hono-bun.md)
//   @hono/node-server  -- Hono adapter for Node.js HTTP server
//
// Environment variables:
//   NATS_URL   NATS server URL (default: nats://nats:4222)
//   PORT       HTTP listen port (default: 3000)

import { connect, NatsConnection, StringCodec } from "nats";
import { Hono } from "hono";
import { serve } from "@hono/node-server";

const NATS_URL = process.env.NATS_URL ?? "nats://nats:4222";
const PORT = parseInt(process.env.PORT ?? "3000", 10);

const sc = StringCodec();

// Module-level connection reference — used by the health endpoint.
let natsConn: NatsConnection | null = null;

async function main() {
  // --- NATS connection ---
  console.log(`Connecting to NATS at ${NATS_URL}`);
  const nc = await connect({ servers: NATS_URL });
  natsConn = nc;
  console.log("NATS connected");

  // --- Subscribe to state updates from Elixir ---
  // Subject pattern "state.*.updates" matches all doc state broadcasts.
  // Elixir publishes to "state.{doc_id}.updates" when it processes a client action.
  const stateSub = nc.subscribe("state.*.updates");
  console.log("Subscribed to state.*.updates");

  // Process incoming state updates in a background async loop.
  (async () => {
    for await (const msg of stateSub) {
      try {
        const payload = JSON.parse(sc.decode(msg.data)) as Record<string, unknown>;
        console.log(
          `state update received event_type=${payload["event_type"]} ` +
          `doc_id=${payload["doc_id"]} ` +
          `data=${JSON.stringify(payload["data"])}`
        );
      } catch (err) {
        console.warn("failed to decode state update:", err);
      }
    }
  })();

  // --- Publish a demo client action ---
  // Subject: "actions.{session_id}.{action_type}"
  // Elixir subscribes to "actions.>" and processes all client actions.
  const actionSubject = "actions.sess-demo.cursor.moved";
  const actionPayload = {
    payload_version: 1,
    session_id: "sess-demo",
    correlation_id: "demo-001",
    published_at: new Date().toISOString(),
    action_type: "cursor.moved",
    data: {
      x: 100,
      y: 200,
      doc_id: "doc-abc",
    },
  };

  nc.publish(actionSubject, sc.encode(JSON.stringify(actionPayload)));
  console.log(
    `published action to "${actionSubject}" correlation_id=${actionPayload.correlation_id}`
  );

  // --- HTTP /healthz via Hono ---
  const app = new Hono();

  app.get("/healthz", (c) => {
    if (natsConn === null || natsConn.isClosed()) {
      return c.json({ status: "degraded", reason: "nats disconnected" }, 503);
    }
    return c.json({ status: "ok" });
  });

  serve({ fetch: app.fetch, port: PORT }, (info) => {
    console.log(`HTTP healthz listening on port ${info.port}`);
  });

  // Handle graceful shutdown.
  process.on("SIGTERM", async () => {
    console.log("SIGTERM received — draining NATS connection");
    await nc.drain();
    process.exit(0);
  });
}

main().catch((err) => {
  console.error("fatal error:", err);
  process.exit(1);
});
