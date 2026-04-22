import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { pathToFileURL } from "url";

import authRoutes from "./routes/auth.ts";
import meRoutes from "./routes/me.ts";
import usersRoutes from "./routes/users.ts";
import groupsRoutes from "./routes/groups.ts";
import adminRoutes from "./routes/admin.ts";
import permissionsRoutes from "./routes/permissions.ts";
import healthRoutes from "./routes/health.ts";

const app = new Hono();

app.route("/", authRoutes);
app.route("/", meRoutes);
app.route("/", usersRoutes);
app.route("/", groupsRoutes);
app.route("/", adminRoutes);
app.route("/", permissionsRoutes);
app.route("/", healthRoutes);

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  serve({
    fetch: app.fetch,
    port: Number(process.env.PORT || 3000),
  });
}

export default app;
