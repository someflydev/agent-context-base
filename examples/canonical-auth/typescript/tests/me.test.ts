import assert from "node:assert/strict";
import { describe, test } from "node:test";
import { issueToken } from "../src/auth/token.ts";
import { store } from "../src/domain/store.ts";
import app from "../src/index.ts";

process.env.TENANTCORE_TEST_SECRET = "test-secret-12345";
process.env.TENANTCORE_TEST_ALG = "HS256";

const fetchClient = app.fetch;

describe("GET /me Unit Tests", () => {
  test("/me returns correct auth context fields", async () => {
    const user = store.getUserByEmail("alice@acme.example")!;
    const token = await issueToken(user);
    
    const req = new Request("http://localhost/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const res = await fetchClient(req);
    assert.equal(res.status, 200);
    
    const data: any = await res.json();
    assert.equal(data.sub, user.id);
    assert.equal(data.email, user.email);
    assert.equal(data.tenant_id, user.tenant_id);
    assert.equal(Array.isArray(data.allowed_routes), true);
    assert.equal(Array.isArray(data.guide_sections), true);
  });

  test("super_admin /me has correct shape", async () => {
    const user = store.getUserByEmail("superadmin@tenantcore.dev")!;
    const token = await issueToken(user);
    
    const req = new Request("http://localhost/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const res = await fetchClient(req);
    assert.equal(res.status, 200);
    
    const data: any = await res.json();
    assert.equal(data.tenant_id, null);
    assert.equal(data.tenant_role, "super_admin");
    
    // Ensure allowed routes contains admin routes
    const adminRoutes = data.allowed_routes.filter((r: any) => r.path.startsWith("/admin"));
    assert.ok(adminRoutes.length > 0);
  });
});
