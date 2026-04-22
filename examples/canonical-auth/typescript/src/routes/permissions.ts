import { Hono } from "hono";
import { jwtMiddleware, requirePermission } from "../auth/middleware.ts";
import { store } from "../domain/store.ts";

const app = new Hono();

app.use("/permissions", jwtMiddleware);

app.get("/permissions", requirePermission("iam:permission:read"), async (c) => {
  return c.json({ permissions: store.permissions });
});

export default app;
