import { Hono } from "hono";

import authRoutes from "./routes/auth";
import meRoutes from "./routes/me";
import usersRoutes from "./routes/users";
import groupsRoutes from "./routes/groups";
import adminRoutes from "./routes/admin";
import permissionsRoutes from "./routes/permissions";
import healthRoutes from "./routes/health";

const app = new Hono();

app.route("/", authRoutes);
app.route("/", meRoutes);
app.route("/", usersRoutes);
app.route("/", groupsRoutes);
app.route("/", adminRoutes);
app.route("/", permissionsRoutes);
app.route("/", healthRoutes);

export default {
  port: process.env.PORT || 3000,
  fetch: app.fetch,
};
