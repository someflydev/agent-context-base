import assert from "node:assert/strict";
import { describe, test } from "node:test";
import { issueToken, getVerificationKey } from "../src/auth/token.ts";
import { store } from "../src/domain/store.ts";
import { jwtVerify } from "jose";

process.env.TENANTCORE_TEST_SECRET = "test-secret-12345";
process.env.TENANTCORE_TEST_ALG = "HS256";

describe("Token Unit Tests", () => {
  test("issueToken produces a verifiable JWT", async () => {
    const user = store.getUserByEmail("alice@acme.example");
    if (!user) throw new Error("Fixture user missing");

    const token = await issueToken(user, store);
    assert.ok(token);

    const key = await getVerificationKey();
    const { payload } = await jwtVerify(token, key, {
      issuer: "tenantcore-auth",
      audience: "tenantcore-api",
    });

    assert.equal(payload.iss, "tenantcore-auth");
    assert.equal(payload.aud, "tenantcore-api");
    assert.equal(payload.sub, user.id);
    assert.equal((payload.exp as number) - (payload.iat as number), 900);
    assert.equal(payload.tenant_id, user.tenant_id);
    assert.equal(payload.tenant_role, "tenant_member");
    assert.equal(Array.isArray(payload.groups), true);
    assert.equal(Array.isArray(payload.permissions), true);
    assert.equal(payload.acl_ver, user.acl_ver);
  });

  test("super_admin token shape", async () => {
    const user = store.getUserByEmail("superadmin@tenantcore.dev");
    if (!user) throw new Error("Fixture user missing");

    const token = await issueToken(user, store);
    
    const key = await getVerificationKey();
    const { payload } = await jwtVerify(token, key, {
      issuer: "tenantcore-auth",
      audience: "tenantcore-api",
    });

    assert.equal(payload.tenant_id, undefined);
    assert.equal(payload.tenant_role, "super_admin");
  });
});
