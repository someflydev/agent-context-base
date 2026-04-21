import { expect, test, describe } from "bun:test";
import { issueToken, getVerificationKey } from "../src/auth/token";
import { store } from "../src/domain/store";
import { jwtVerify } from "jose";

process.env.TENANTCORE_TEST_SECRET = "test-secret-12345";
process.env.TENANTCORE_TEST_ALG = "HS256";

describe("Token Unit Tests", () => {
  test("issueToken produces a verifiable JWT", async () => {
    const user = store.getUserByEmail("alice@acme.example");
    if (!user) throw new Error("Fixture user missing");

    const token = await issueToken(user, store);
    expect(token).toBeTruthy();

    const key = await getVerificationKey();
    const { payload } = await jwtVerify(token, key, {
      issuer: "tenantcore-auth",
      audience: "tenantcore-api",
    });

    expect(payload.iss).toBe("tenantcore-auth");
    expect(payload.aud).toBe("tenantcore-api");
    expect(payload.sub).toBe(user.id);
    expect((payload.exp as number) - (payload.iat as number)).toBe(900);
    expect(payload.tenant_id).toBe(user.tenant_id);
    expect(payload.tenant_role).toBe("tenant_member");
    expect(Array.isArray(payload.groups)).toBe(true);
    expect(Array.isArray(payload.permissions)).toBe(true);
    expect(payload.acl_ver).toBe(user.acl_ver);
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

    expect(payload.tenant_id).toBeUndefined();
    expect(payload.tenant_role).toBe("super_admin");
  });
});
