import { expect, test, describe } from "bun:test";
import { issueToken } from "../src/auth/token";
import { store } from "../src/domain/store";
import app from "../src/index";

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
    expect(res.status).toBe(200);
    
    const data: any = await res.json();
    expect(data.sub).toBe(user.id);
    expect(data.email).toBe(user.email);
    expect(data.tenant_id).toBe(user.tenant_id);
    expect(Array.isArray(data.allowed_routes)).toBe(true);
    expect(Array.isArray(data.guide_sections)).toBe(true);
  });

  test("super_admin /me has correct shape", async () => {
    const user = store.getUserByEmail("superadmin@tenantcore.dev")!;
    const token = await issueToken(user);
    
    const req = new Request("http://localhost/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const res = await fetchClient(req);
    expect(res.status).toBe(200);
    
    const data: any = await res.json();
    expect(data.tenant_id).toBeNull();
    expect(data.tenant_role).toBe("super_admin");
    
    // Ensure allowed routes contains admin routes
    const adminRoutes = data.allowed_routes.filter((r: any) => r.path.startsWith("/admin"));
    expect(adminRoutes.length).toBeGreaterThan(0);
  });
});
