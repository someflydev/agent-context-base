<?php
declare(strict_types=1);

namespace AgentContextBase\Faker\Pipeline;

use AgentContextBase\Faker\Domain\Dataset;
use AgentContextBase\Faker\Domain\Organization;
use AgentContextBase\Faker\Domain\User;
use AgentContextBase\Faker\Domain\Membership;
use AgentContextBase\Faker\Domain\Project;
use AgentContextBase\Faker\Domain\AuditEvent;
use AgentContextBase\Faker\Domain\ApiKey;
use AgentContextBase\Faker\Domain\Invitation;
use AgentContextBase\Faker\Pools\IdPools;
use AgentContextBase\Faker\Profiles\Profile;
use AgentContextBase\Faker\Distributions\Distributions;
use Faker\Factory;
use Faker\Generator;
use Random\Randomizer;
use Random\Engine\Mt19937;
use DateTimeImmutable;
use DateInterval;

final class TenantCorePipeline {
    private Generator $faker;
    private Randomizer $rng;
    private IdPools $pools;

    public function __construct(
        private readonly Profile $profile,
        private readonly int $seed = 42
    ) {
        $this->faker = Factory::create('en_US');
        $this->faker->seed($this->seed);
        $this->rng = new Randomizer(new Mt19937($this->seed));
        $this->pools = new IdPools();
    }

    public function generate(): Dataset {
        $numOrgs = $this->profile->numOrgs;
        $numUsers = max(10, (int)($numOrgs * 3.3)); // Rough approximation based on Profile

        $organizations = $this->buildOrganizations($numOrgs);
        $users = $this->buildUsers($numUsers);
        $memberships = $this->buildMemberships($organizations, $users);
        $projects = $this->buildProjects($organizations);
        $api_keys = $this->buildApiKeys($organizations);
        $invitations = $this->buildInvitations($organizations, $users);
        $audit_events = $this->buildAuditEvents($organizations, $projects, $memberships, $api_keys, $invitations);

        return new Dataset(
            organizations: $organizations,
            users: $users,
            memberships: $memberships,
            projects: $projects,
            audit_events: $audit_events,
            api_keys: $api_keys,
            invitations: $invitations,
        );
    }

    /**
     * @return Organization[]
     */
    private function buildOrganizations(int $count): array {
        $orgs = [];
        $weights = ['free' => 50, 'pro' => 35, 'enterprise' => 15];
        $regions = ['us-east' => 40, 'us-west' => 25, 'eu-west' => 20, 'ap-southeast' => 15];

        $this->faker->unique(true); // reset uniqueness tracker
        
        for ($i = 0; $i < $count; $i++) {
            $name = $this->faker->unique()->company();
            $slug = strtolower(preg_replace('/[^a-zA-Z0-9]+/', '-', $name));
            $org = new Organization(
                id: $this->faker->uuid(),
                name: $name,
                slug: trim($slug, '-'),
                plan: Distributions::weightedChoice($weights, $this->rng),
                region: Distributions::weightedChoice($regions, $this->rng),
                created_at: $this->faker->dateTimeBetween('-3 years', '-1 years')->format('Y-m-d\TH:i:s\Z'),
                owner_email: $this->faker->unique()->companyEmail(),
            );
            $orgs[] = $org;
            $this->pools->orgIds[] = $org->id;
            $this->pools->orgMembers[$org->id] = [];
            $this->pools->projectIds[$org->id] = [];
            $this->pools->memberEmails[$org->id] = [];
        }
        return $orgs;
    }

    /**
     * @return User[]
     */
    private function buildUsers(int $count): array {
        $users = [];
        $locales = ['en-US' => 60, 'en-GB' => 20, 'de-DE' => 10, 'fr-FR' => 10];
        $timezones = ['en-US' => 'America/New_York', 'en-GB' => 'Europe/London', 'de-DE' => 'Europe/Berlin', 'fr-FR' => 'Europe/Paris'];

        $this->faker->unique(true); // reset unique emails
        for ($i = 0; $i < $count; $i++) {
            $locale = Distributions::weightedChoice($locales, $this->rng);
            $user = new User(
                id: $this->faker->uuid(),
                email: clone $this->faker->unique()->safeEmail(),
                full_name: $this->faker->name(),
                locale: $locale,
                timezone: $timezones[$locale],
                created_at: $this->faker->dateTimeBetween('-3 years', '-1 years')->format('Y-m-d\TH:i:s\Z'),
            );
            $users[] = $user;
            $this->pools->userIds[] = $user->id;
        }
        return $users;
    }

    /**
     * @param Organization[] $orgs
     * @param User[] $users
     * @return Membership[]
     */
    private function buildMemberships(array $orgs, array $users): array {
        $memberships = [];
        $roles = ['admin' => 10, 'member' => 60, 'viewer' => 25];

        foreach ($orgs as $org) {
            $memberCount = $this->rng->getInt(3, min(50, count($users)));
            
            $shuffledUserIds = $this->pools->userIds;
            shuffle($shuffledUserIds);
            $selectedUserIds = array_slice($shuffledUserIds, 0, $memberCount);
            
            $orgCreated = new DateTimeImmutable($org->created_at);
            
            $ownerId = $selectedUserIds[0];
            
            $invitedByPool = [];
            
            foreach ($selectedUserIds as $index => $userId) {
                $role = ($index === 0) ? 'owner' : Distributions::weightedChoice($roles, $this->rng);
                
                $days = $this->rng->getInt(0, 365);
                $joinedAt = $orgCreated->add(new DateInterval("P{$days}D"));
                
                $invitedBy = null;
                if ($role !== 'owner' && count($invitedByPool) > 0) {
                    $invitedBy = $invitedByPool[array_rand($invitedByPool)];
                }
                
                $membership = new Membership(
                    id: $this->faker->uuid(),
                    org_id: $org->id,
                    user_id: $userId,
                    role: $role,
                    joined_at: $joinedAt->format('Y-m-d\TH:i:s\Z'),
                    invited_by: $invitedBy,
                );
                
                $memberships[] = $membership;
                $this->pools->orgMembers[$org->id][$userId] = $role;
                
                $userEmail = '';
                foreach ($users as $u) {
                    if ($u->id === $userId) {
                        $userEmail = $u->email;
                        break;
                    }
                }
                $this->pools->memberEmails[$org->id][strtolower($userEmail)] = $userId;
                
                $invitedByPool[] = $userId;
            }
        }
        
        return $memberships;
    }

    /**
     * @param Organization[] $orgs
     * @return Project[]
     */
    private function buildProjects(array $orgs): array {
        $projects = [];
        $statuses = ['active' => 60, 'archived' => 25, 'draft' => 15];
        
        foreach ($orgs as $org) {
            $count = $this->rng->getInt(1, 10);
            $orgCreated = new DateTimeImmutable($org->created_at);
            $orgMemberIds = array_keys($this->pools->orgMembers[$org->id]);
            
            if (empty($orgMemberIds)) continue;
            
            for ($i = 0; $i < $count; $i++) {
                $days = $this->rng->getInt(0, 100);
                $createdAt = $orgCreated->add(new DateInterval("P{$days}D"));
                $createdBy = $orgMemberIds[array_rand($orgMemberIds)];
                
                $project = new Project(
                    id: $this->faker->uuid(),
                    org_id: $org->id,
                    name: $this->faker->catchPhrase(),
                    status: Distributions::weightedChoice($statuses, $this->rng),
                    created_by: $createdBy,
                    created_at: $createdAt->format('Y-m-d\TH:i:s\Z'),
                );
                $projects[] = $project;
                $this->pools->projectIds[$org->id][] = $project->id;
            }
        }
        return $projects;
    }

    /**
     * @param Organization[] $orgs
     * @return ApiKey[]
     */
    private function buildApiKeys(array $orgs): array {
        $api_keys = [];
        $seenPrefixes = [];
        
        foreach ($orgs as $org) {
            $count = $this->rng->getInt(0, 5);
            $orgCreated = new DateTimeImmutable($org->created_at);
            $orgMemberIds = array_keys($this->pools->orgMembers[$org->id]);
            
            if (empty($orgMemberIds)) continue;
            
            for ($i = 0; $i < $count; $i++) {
                $suffix = substr(str_shuffle("abcdefghijklmnopqrstuvwxyz0123456789"), 0, 8);
                $prefix = "tc_$suffix";
                while (isset($seenPrefixes[$prefix])) {
                    $suffix = substr(str_shuffle("abcdefghijklmnopqrstuvwxyz0123456789"), 0, 8);
                    $prefix = "tc_$suffix";
                }
                $seenPrefixes[$prefix] = true;
                
                $days = $this->rng->getInt(0, 100);
                $createdAt = $orgCreated->add(new DateInterval("P{$days}D"));
                
                $lastUsedAt = null;
                if ($this->rng->getInt(1, 100) > 50) {
                    $usedDays = $this->rng->getInt(0, 50);
                    $lastUsedAt = clone $createdAt;
                    $lastUsedAt = $lastUsedAt->add(new DateInterval("P{$usedDays}D"))->format('Y-m-d\TH:i:s\Z');
                }
                
                $api_keys[] = new ApiKey(
                    id: $this->faker->uuid(),
                    org_id: $org->id,
                    created_by: $orgMemberIds[array_rand($orgMemberIds)],
                    name: $this->faker->word() . " key",
                    key_prefix: $prefix,
                    created_at: $createdAt->format('Y-m-d\TH:i:s\Z'),
                    last_used_at: $lastUsedAt,
                );
            }
        }
        return $api_keys;
    }

    /**
     * @param Organization[] $orgs
     * @param User[] $users
     * @return Invitation[]
     */
    private function buildInvitations(array $orgs, array $users): array {
        $invitations = [];
        $roles = ['admin' => 15, 'member' => 65, 'viewer' => 20];
        
        foreach ($orgs as $org) {
            $count = $this->rng->getInt(0, 3);
            $orgMemberIds = array_keys($this->pools->orgMembers[$org->id]);
            if (empty($orgMemberIds)) continue;
            
            for ($i = 0; $i < $count; $i++) {
                $invitedEmail = strtolower($this->faker->email());
                while (isset($this->pools->memberEmails[$org->id][$invitedEmail])) {
                    $invitedEmail = strtolower($this->faker->email());
                }
                
                $acceptedAt = null;
                if ($this->rng->getInt(1, 100) <= 40) {
                    $acceptedAt = $this->faker->dateTimeBetween('-1 years', 'now')->format('Y-m-d\TH:i:s\Z');
                }
                
                $invitations[] = new Invitation(
                    id: $this->faker->uuid(),
                    org_id: $org->id,
                    invited_email: $invitedEmail,
                    role: Distributions::weightedChoice($roles, $this->rng),
                    invited_by: $orgMemberIds[array_rand($orgMemberIds)],
                    expires_at: $this->faker->dateTimeBetween('now', '+30 days')->format('Y-m-d\TH:i:s\Z'),
                    accepted_at: $acceptedAt,
                );
            }
        }
        return $invitations;
    }

    /**
     * @param Organization[] $orgs
     * @param Project[] $projects
     * @param Membership[] $memberships
     * @param ApiKey[] $api_keys
     * @param Invitation[] $invitations
     * @return AuditEvent[]
     */
    private function buildAuditEvents(array $orgs, array $projects, array $memberships, array $api_keys, array $invitations): array {
        $events = [];
        $actions = ['updated' => 35, 'created' => 20, 'exported' => 15, 'invited' => 12, 'archived' => 10, 'deleted' => 8];
        
        $membership_joined = [];
        foreach ($memberships as $m) {
            $membership_joined["{$m->org_id}:{$m->user_id}"] = new DateTimeImmutable($m->joined_at);
        }
        
        foreach ($projects as $project) {
            $orgMemberIds = array_keys($this->pools->orgMembers[$project->org_id]);
            if (empty($orgMemberIds)) continue;
            
            $count = $this->rng->getInt(2, 10);
            $projectCreated = new DateTimeImmutable($project->created_at);
            
            for ($i = 0; $i < $count; $i++) {
                $userId = $orgMemberIds[array_rand($orgMemberIds)];
                
                $joinedAt = $membership_joined["{$project->org_id}:{$userId}"] ?? $projectCreated;
                $floor = $projectCreated > $joinedAt ? $projectCreated : $joinedAt;
                
                $days = $this->rng->getInt(0, 365);
                $ts = $floor->add(new DateInterval("P{$days}D"));
                
                $events[] = new AuditEvent(
                    id: $this->faker->uuid(),
                    org_id: $project->org_id,
                    user_id: $userId,
                    project_id: $project->id,
                    action: Distributions::weightedChoice($actions, $this->rng),
                    resource_type: 'project',
                    resource_id: $project->id,
                    ts: $ts->format('Y-m-d\TH:i:s\Z'),
                );
            }
        }
        
        return $events;
    }
}
