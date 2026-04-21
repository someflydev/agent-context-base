import { Hono } from "hono";
import { jwtMiddleware, requirePermission } from "../auth/middleware";
import { store } from "../domain/store";

const app = new Hono();

app.use("*", jwtMiddleware, requirePermission("iam:permission:read"));

app.get("/permissions", async (c) => {
  return c.json({ permissions: store.permissions });
});

export default app;
