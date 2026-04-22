import assert from "node:assert/strict";
import { describe, test } from "node:test";
import { issueToken } from "../src/auth/token.ts";
import { store } from "../src/domain/store.ts";
import app from "../src/index.ts";

process.env.TENANTCORE_TEST_SECRET = "test-secret-12345";
process.env.TENANTCORE_TEST_ALG = "HS256";

const fetchClient = app.fetch;

describe("Auth Flow Smoke Tests", () => {
  test("Flow 1: Issue Token", async () => {
    const req = new Request("http://localhost/auth/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "alice@acme.example", password: "password" }),
    });
    const res = await fetchClient(req);
    assert.equal(res.status, 200);
    const data: any = await res.json();
    assert.ok(data.access_token);
  });

  test("Flow 2: GET /me", async () => {
    const user = store.getUserByEmail("alice@acme.example")!;
    const token = await issueToken(user);
    
    const req = new Request("http://localhost/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const res = await fetchClient(req);
    assert.equal(res.status, 200);
  });

  test("Flow 3: Super Admin - Create Tenant", async () => {
    const admin = store.getUserByEmail("superadmin@tenantcore.dev")!;
    const token = await issueToken(admin);
    
    const req = new Request("http://localhost/admin/tenants", {
      method: "POST",
      headers: { 
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: "New Tenant TS",
        slug: "new-tenant-ts",
        admin_email: "admin@newtenantts.example"
      })
    });
    const res = await fetchClient(req);
    assert.equal(res.status, 200);
  });

  test("Flow 4: Tenant Admin - Create Group", async () => {
    const acmeAdmin = store.getUserByEmail("admin@acme.example")!;
    const token = await issueToken(acmeAdmin);
    
    const req = new Request("http://localhost/groups", {
      method: "POST",
      headers: { 
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: "New Group",
        slug: "new-group"
      })
    });
    const res = await fetchClient(req);
    assert.equal(res.status, 200);
  });

  test("Flow 5: Tenant Admin - Assign Permission", async () => {
    const acmeAdmin = store.getUserByEmail("admin@acme.example")!;
    const token = await issueToken(acmeAdmin);
    
    const groupReq = new Request("http://localhost/groups", {
      method: "POST",
      headers: { 
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name: "Perm Group", slug: "perm-group" })
    });
    const groupRes = await fetchClient(groupReq);
    const group: any = await groupRes.json();

    const permRes = await fetchClient(new Request("http://localhost/permissions", {
      headers: { Authorization: `Bearer ${token}` }
    }));
    const permData: any = await permRes.json();
    const permId = permData.permissions[0].id;

    const assignReq = new Request(`http://localhost/groups/${group.id}/permissions`, {
      method: "POST",
      headers: { 
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ permission_id: permId })
    });
    const assignRes = await fetchClient(assignReq);
    assert.equal(assignRes.status, 200);
  });

  test("Flow 6: Tenant Admin - Invite User", async () => {
    const acmeAdmin = store.getUserByEmail("admin@acme.example")!;
    const token = await issueToken(acmeAdmin);
    
    const req = new Request("http://localhost/users", {
      method: "POST",
      headers: { 
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email: "newuser@acme.example",
        display_name: "New User"
      })
    });
    const res = await fetchClient(req);
    assert.equal(res.status, 200);
  });

  test("Flow 7: Tenant Admin - Assign User to Group", async () => {
    const acmeAdmin = store.getUserByEmail("admin@acme.example")!;
    const token = await issueToken(acmeAdmin);
    
    const groupReq = new Request("http://localhost/groups", {
      method: "POST",
      headers: { 
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name: "User Group", slug: "user-group" })
    });
    const groupRes = await fetchClient(groupReq);
    const group: any = await groupRes.json();

    const userReq = new Request("http://localhost/users", {
      method: "POST",
      headers: { 
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email: "newuser2@acme.example", display_name: "New User 2" })
    });
    const userRes = await fetchClient(userReq);
    const user: any = await userRes.json();

    const assignReq = new Request(`http://localhost/groups/${group.id}/users`, {
      method: "POST",
      headers: { 
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ user_id: user.id })
    });
    const assignRes = await fetchClient(assignReq);
    assert.equal(assignRes.status, 200);
  });

  test("Flow 8: Tenant Member - Read Users", async () => {
    const acmeMember = store.getUserByEmail("alice@acme.example")!;
    const token = await issueToken(acmeMember);
    
    const req = new Request("http://localhost/users", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const res = await fetchClient(req);
    assert.ok([200, 403].includes(res.status));
  });

  test("Flow 9: Cross-Tenant Denial", async () => {
    const acmeAdmin = store.getUserByEmail("admin@acme.example")!;
    const globexMember = store.getUserByEmail("carol@globex.example")!;
    const token = await issueToken(acmeAdmin);
    
    const req = new Request(`http://localhost/users/${globexMember.id}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const res = await fetchClient(req);
    assert.equal(res.status, 403);
  });

  test("Flow 10: Stale ACL Version Denial", async () => {
    const acmeMember = store.getUserByEmail("alice@acme.example")!;
    const token = await issueToken(acmeMember);
    
    acmeMember.acl_ver += 1;
    
    const req = new Request("http://localhost/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    const res = await fetchClient(req);
    assert.equal(res.status, 401);
  });
});
