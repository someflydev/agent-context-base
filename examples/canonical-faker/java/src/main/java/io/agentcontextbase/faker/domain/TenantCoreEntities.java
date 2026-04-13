package io.agentcontextbase.faker.domain;

import java.util.List;

public final class TenantCoreEntities {
    private TenantCoreEntities() {
    }

    public record Organization(
            String id,
            String name,
            String slug,
            String plan,
            String region,
            String createdAt,
            String ownerEmail
    ) {
    }

    public record User(
            String id,
            String email,
            String fullName,
            String locale,
            String timezone,
            String createdAt
    ) {
    }

    public record Membership(
            String id,
            String orgId,
            String userId,
            String role,
            String joinedAt,
            String invitedBy
    ) {
    }

    public record Project(
            String id,
            String orgId,
            String name,
            String status,
            String createdBy,
            String createdAt
    ) {
    }

    public record AuditEvent(
            String id,
            String orgId,
            String userId,
            String projectId,
            String action,
            String resourceType,
            String resourceId,
            String ts
    ) {
    }

    public record ApiKey(
            String id,
            String orgId,
            String createdBy,
            String name,
            String keyPrefix,
            String createdAt,
            String lastUsedAt
    ) {
    }

    public record Invitation(
            String id,
            String orgId,
            String invitedEmail,
            String role,
            String invitedBy,
            String expiresAt,
            String acceptedAt
    ) {
    }

    public record TenantCoreDataset(
            String profileName,
            long seed,
            List<Organization> organizations,
            List<User> users,
            List<Membership> memberships,
            List<Project> projects,
            List<AuditEvent> auditEvents,
            List<ApiKey> apiKeys,
            List<Invitation> invitations
    ) {
    }
}
