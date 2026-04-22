import { SignJWT, generateKeyPair, exportJWK, importJWK } from "jose";
import { InMemoryStore, store as globalStore } from "../domain/store.ts";
import type { User } from "../domain/models.ts";

let _privateKey: any;
let _publicKey: any;
let keysGenerated = false;

async function getKeys() {
  if (!keysGenerated) {
    const { publicKey, privateKey } = await generateKeyPair("ES256", { extractable: true });
    _privateKey = privateKey;
    _publicKey = publicKey;
    keysGenerated = true;
  }
  return { privateKey: _privateKey, publicKey: _publicKey };
}

export async function getVerificationKey() {
  const secret = process.env.TENANTCORE_TEST_SECRET;
  if (secret && process.env.TENANTCORE_TEST_ALG === "HS256") {
    return new TextEncoder().encode(secret);
  }
  const keys = await getKeys();
  return keys.publicKey;
}

export async function getSigningKey() {
  const secret = process.env.TENANTCORE_TEST_SECRET;
  if (secret && process.env.TENANTCORE_TEST_ALG === "HS256") {
    return new TextEncoder().encode(secret);
  }
  const keys = await getKeys();
  return keys.privateKey;
}

export async function issueToken(user: User, store: InMemoryStore = globalStore): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  const exp = now + 15 * 60; // 15 minutes

  const membership = store.memberships.find(
    (m) => m.user_id === user.id && m.is_active
  );

  let tenantId: string | null = null;
  let tenantRole: "super_admin" | "tenant_admin" | "tenant_member" = "tenant_member";

  if (membership) {
    tenantId = membership.tenant_id;
    tenantRole = membership.tenant_role;
  } else if (user.tenant_id === null) {
    tenantRole = "super_admin";
  }

  const groups = store.getGroupsForUser(user.id, tenantId);
  let permissions = store.getEffectivePermissions(user.id);

  if (tenantRole === "tenant_admin") {
    permissions = store.permissions.map(p => p.name);
  }
  if (tenantRole === "super_admin") {
    permissions = store.permissions.filter(p => p.name.startsWith("admin:")).map(p => p.name);
  }

  const payload: any = {
    iss: "tenantcore-auth",
    aud: "tenantcore-api",
    sub: user.id,
    exp,
    iat: now,
    nbf: now,
    jti: crypto.randomUUID(),
    tenant_role: tenantRole,
    groups: groups.map((g) => g.slug),
    permissions,
    acl_ver: user.acl_ver,
  };

  if (tenantId) {
    payload.tenant_id = tenantId;
  }

  const alg = process.env.TENANTCORE_TEST_ALG === "HS256" && process.env.TENANTCORE_TEST_SECRET ? "HS256" : "ES256";
  const key = await getSigningKey();

  return new SignJWT(payload)
    .setProtectedHeader({ alg })
    .sign(key);
}
