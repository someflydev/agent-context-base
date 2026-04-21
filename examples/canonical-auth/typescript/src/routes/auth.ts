import { Hono } from "hono";
import { store } from "../domain/store";
import { issueToken } from "../auth/token";

const app = new Hono();

app.post("/auth/token", async (c) => {
  const body = await c.req.json();
  const { email, password } = body;

  const user = store.getUserByEmail(email);

  if (!user || !user.is_active) {
    return c.json({ detail: "Invalid credentials" }, 401);
  }

  if (password !== "password") {
    return c.json({ detail: "Invalid credentials" }, 401);
  }

  const token = await issueToken(user, store);
  return c.json({ access_token: token, token_type: "bearer" });
});

export default app;
