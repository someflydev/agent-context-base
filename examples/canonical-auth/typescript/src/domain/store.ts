import { readFileSync } from "fs";
import { join } from "path";
import { fileURLToPath } from "url";
import type {
  User,
  Tenant,
  Membership,
  Group,
  Permission,
  GroupPermission,
  UserGroup,
} from "./models.ts";

const fixturesDir = join(
  fileURLToPath(new URL(".", import.meta.url)),
  "../../..",
  "domain",
  "fixtures"
);

export class InMemoryStore {
  public users: User[] = [];
  public tenants: Tenant[] = [];
  public memberships: Membership[] = [];
  public groups: Group[] = [];
  public permissions: Permission[] = [];
  public group_permissions: GroupPermission[] = [];
  public user_groups: UserGroup[] = [];

  constructor() {
    this._loadFixtures();
  }

  private _loadFixtures() {
    const loadJson = (filename: string) => {
      const data = readFileSync(join(fixturesDir, filename), "utf8");
      return JSON.parse(data);
    };

    this.users = loadJson("users.json");
    this.tenants = loadJson("tenants.json");
    this.memberships = loadJson("memberships.json");
    this.groups = loadJson("groups.json");
    this.permissions = loadJson("permissions.json");
    this.group_permissions = loadJson("group_permissions.json");
    this.user_groups = loadJson("user_groups.json");
  }

  public getUserById(userId: string): User | undefined {
    return this.users.find((u) => u.id === userId);
  }

  public getUserByEmail(email: string): User | undefined {
    return this.users.find((u) => u.email === email);
  }

  public getTenantById(tenantId: string): Tenant | undefined {
    return this.tenants.find((t) => t.id === tenantId);
  }

  public getGroupsForUser(userId: string, tenantId: string | null): Group[] {
    const userGroupIds = new Set(
      this.user_groups.filter((ug) => ug.user_id === userId).map((ug) => ug.group_id)
    );
    if (tenantId) {
      return this.groups.filter(
        (g) => userGroupIds.has(g.id) && g.tenant_id === tenantId
      );
    }
    return this.groups.filter((g) => userGroupIds.has(g.id));
  }

  public getEffectivePermissions(userId: string): string[] {
    const userGroupIds = new Set(
      this.user_groups.filter((ug) => ug.user_id === userId).map((ug) => ug.group_id)
    );
    const permissionIds = new Set(
      this.group_permissions
        .filter((gp) => userGroupIds.has(gp.group_id))
        .map((gp) => gp.permission_id)
    );
    return this.permissions
      .filter((p) => permissionIds.has(p.id))
      .map((p) => p.name);
  }

  public verifyMembership(userId: string, tenantId: string): boolean {
    const membership = this.memberships.find(
      (m) => m.user_id === userId && m.tenant_id === tenantId
    );
    return membership !== undefined && membership.is_active;
  }

  public getTenantName(tenantId: string): string | null {
    const t = this.getTenantById(tenantId);
    return t ? t.name : null;
  }
}

export const store = new InMemoryStore();
