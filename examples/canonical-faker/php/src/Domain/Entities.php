<?php
declare(strict_types=1);

namespace AgentContextBase\Faker\Domain;

final readonly class Organization {
    public function __construct(
        public string $id,
        public string $name,
        public string $slug,
        public string $plan,
        public string $region,
        public string $created_at,
        public string $owner_email,
    ) {}
    public function toArray(): array { return get_object_vars($this); }
}

final readonly class User {
    public function __construct(
        public string $id,
        public string $email,
        public string $full_name,
        public string $locale,
        public string $timezone,
        public string $created_at,
    ) {}
    public function toArray(): array { return get_object_vars($this); }
}

final readonly class Membership {
    public function __construct(
        public string $id,
        public string $org_id,
        public string $user_id,
        public string $role,
        public string $joined_at,
        public ?string $invited_by,
    ) {}
    public function toArray(): array { return get_object_vars($this); }
}

final readonly class Project {
    public function __construct(
        public string $id,
        public string $org_id,
        public string $name,
        public string $status,
        public string $created_by,
        public string $created_at,
    ) {}
    public function toArray(): array { return get_object_vars($this); }
}

final readonly class AuditEvent {
    public function __construct(
        public string $id,
        public string $org_id,
        public string $user_id,
        public string $project_id,
        public string $action,
        public string $resource_type,
        public string $resource_id,
        public string $ts,
    ) {}
    public function toArray(): array { return get_object_vars($this); }
}

final readonly class ApiKey {
    public function __construct(
        public string $id,
        public string $org_id,
        public string $created_by,
        public string $name,
        public string $key_prefix,
        public string $created_at,
        public ?string $last_used_at,
    ) {}
    public function toArray(): array { return get_object_vars($this); }
}

final readonly class Invitation {
    public function __construct(
        public string $id,
        public string $org_id,
        public string $invited_email,
        public string $role,
        public string $invited_by,
        public string $expires_at,
        public ?string $accepted_at,
    ) {}
    public function toArray(): array { return get_object_vars($this); }
}

final readonly class Dataset {
    /**
     * @param Organization[] $organizations
     * @param User[] $users
     * @param Membership[] $memberships
     * @param Project[] $projects
     * @param AuditEvent[] $audit_events
     * @param ApiKey[] $api_keys
     * @param Invitation[] $invitations
     */
    public function __construct(
        public array $organizations,
        public array $users,
        public array $memberships,
        public array $projects,
        public array $audit_events,
        public array $api_keys,
        public array $invitations,
    ) {}
}
