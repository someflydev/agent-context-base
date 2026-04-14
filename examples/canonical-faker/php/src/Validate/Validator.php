<?php
declare(strict_types=1);

namespace AgentContextBase\Faker\Validate;

use AgentContextBase\Faker\Domain\Dataset;
use DateTimeImmutable;

final readonly class ValidationReport {
    public function __construct(
        public bool $ok,
        public array $violations,
        public array $counts,
        public int $seed,
        public string $profile_name,
    ) {}
}

final class Validator {
    private const BASE_TIME = '2026-01-01T12:00:00Z';

    public static function check(Dataset $dataset, int $seed = -1, string $profile_name = 'unknown'): ValidationReport {
        $violations = [];
        $counts = [
            'organizations' => count($dataset->organizations),
            'users' => count($dataset->users),
            'memberships' => count($dataset->memberships),
            'projects' => count($dataset->projects),
            'audit_events' => count($dataset->audit_events),
            'api_keys' => count($dataset->api_keys),
            'invitations' => count($dataset->invitations),
        ];

        $minimum_rows = [
            'organizations' => 1,
            'users' => 1,
            'memberships' => 1,
            'projects' => 1,
            'audit_events' => 1,
            'api_keys' => 0,
            'invitations' => 0,
        ];

        foreach ($minimum_rows as $entity => $min) {
            if ($counts[$entity] < $min) {
                $violations[] = "row count below minimum for $entity: {$counts[$entity]} < $min";
            }
        }

        $orgs = [];
        $seen_org_ids = [];
        foreach ($dataset->organizations as $org) {
            if (isset($seen_org_ids[$org->id])) {
                $violations[] = "duplicate organizations.id: {$org->id}";
            }
            $seen_org_ids[$org->id] = true;
            $orgs[$org->id] = $org;
        }

        $users = [];
        $seen_emails = [];
        foreach ($dataset->users as $user) {
            $email = strtolower($user->email);
            if (isset($seen_emails[$email])) {
                $violations[] = "duplicate user.email: {$email}";
            }
            $seen_emails[$email] = true;
            $users[$user->id] = $user;
        }

        $org_members = [];
        $member_emails = [];
        $membership_joined_at = [];
        
        foreach ($dataset->memberships as $membership) {
            $org = $orgs[$membership->org_id] ?? null;
            $user = $users[$membership->user_id] ?? null;
            
            if ($org === null) {
                $violations[] = "membership missing org: {$membership->id}";
                continue;
            }
            if ($user === null) {
                $violations[] = "membership missing user: {$membership->id}";
                continue;
            }
            
            $org_members[$org->id][$user->id] = true;
            $member_emails[$org->id][strtolower($user->email)] = true;
            
            $joined_at = new DateTimeImmutable($membership->joined_at);
            $membership_joined_at["{$org->id}:{$user->id}"] = $joined_at;
            
            $org_created = new DateTimeImmutable($org->created_at);
            if ($joined_at < $org_created) {
                $violations[] = "Rule A violated by membership {$membership->id}";
            }
            
            if ($membership->invited_by !== null && !isset($users[$membership->invited_by])) {
                $violations[] = "membership invited_by missing user: {$membership->id}";
            }
        }

        $projects = [];
        foreach ($dataset->projects as $project) {
            $projects[$project->id] = $project;
            $org = $orgs[$project->org_id] ?? null;
            if ($org === null) {
                $violations[] = "project missing org: {$project->id}";
                continue;
            }
            
            $project_created = new DateTimeImmutable($project->created_at);
            $org_created = new DateTimeImmutable($org->created_at);
            if ($project_created < $org_created) {
                $violations[] = "Rule B violated by project {$project->id}";
            }
            
            if (!isset($org_members[$project->org_id][$project->created_by])) {
                $violations[] = "Rule C violated by project {$project->id}";
            }
        }
        
        $api_key_ids = [];
        $seen_key_prefixes = [];
        foreach ($dataset->api_keys as $api_key) {
            $api_key_ids[$api_key->id] = true;
            if (!isset($org_members[$api_key->org_id][$api_key->created_by])) {
                $violations[] = "Rule G violated by api_key {$api_key->id}";
            }
            
            if (isset($seen_key_prefixes[$api_key->key_prefix])) {
                $violations[] = "duplicate api_key.key_prefix: {$api_key->key_prefix}";
            }
            $seen_key_prefixes[$api_key->key_prefix] = true;
            
            if ($api_key->last_used_at !== null) {
                $created_at = new DateTimeImmutable($api_key->created_at);
                $last_used = new DateTimeImmutable($api_key->last_used_at);
                if ($last_used < $created_at) {
                    $violations[] = "api_key last_used_at before created_at: {$api_key->id}";
                }
            }
        }
        
        $invitation_ids = [];
        $base_time = new DateTimeImmutable(self::BASE_TIME);
        foreach ($dataset->invitations as $invitation) {
            $invitation_ids[$invitation->id] = true;
            if (!isset($org_members[$invitation->org_id][$invitation->invited_by])) {
                $violations[] = "Rule H violated by invitation {$invitation->id}";
            }
            
            $invited_email = strtolower($invitation->invited_email);
            if (isset($member_emails[$invitation->org_id][$invited_email])) {
                $violations[] = "Rule I violated by invitation {$invitation->id}";
            }
            
            $expires = new DateTimeImmutable($invitation->expires_at);
            if ($expires <= $base_time) {
                $violations[] = "invitation expiry must be in the future: {$invitation->id}";
            }
            
            if ($invitation->accepted_at !== null) {
                $accepted = new DateTimeImmutable($invitation->accepted_at);
                if ($accepted > $base_time) {
                    $violations[] = "invitation accepted_at must be in the past: {$invitation->id}";
                }
            }
        }
        
        $membership_ids = [];
        foreach ($dataset->memberships as $m) $membership_ids[$m->id] = true;

        foreach ($dataset->audit_events as $event) {
            $org = $orgs[$event->org_id] ?? null;
            $project = $projects[$event->project_id] ?? null;
            
            if ($org === null) {
                $violations[] = "audit event missing org: {$event->id}";
                continue;
            }
            if ($project === null) {
                $violations[] = "audit event missing project: {$event->id}";
                continue;
            }
            
            if (!isset($org_members[$event->org_id][$event->user_id])) {
                $violations[] = "Rule D violated by audit event {$event->id}";
            }
            if ($project->org_id !== $event->org_id) {
                $violations[] = "Rule E violated by audit event {$event->id}";
            }
            
            $event_ts = new DateTimeImmutable($event->ts);
            $project_created = new DateTimeImmutable($project->created_at);
            if ($event_ts < $project_created) {
                $violations[] = "Rule F violated by audit event {$event->id}";
            }
            
            $joined_at = $membership_joined_at["{$event->org_id}:{$event->user_id}"] ?? null;
            if ($joined_at !== null && $event_ts < $joined_at) {
                $violations[] = "audit event before membership joined_at: {$event->id}";
            }
            
            $type = $event->resource_type;
            $rid = $event->resource_id;
            if ($type === 'project' && !isset($projects[$rid])) {
                $violations[] = "audit event resource project missing: {$event->id}";
            } elseif ($type === 'user' && !isset($users[$rid])) {
                $violations[] = "audit event resource user missing: {$event->id}";
            } elseif ($type === 'membership' && !isset($membership_ids[$rid])) {
                $violations[] = "audit event resource membership missing: {$event->id}";
            } elseif ($type === 'api_key' && !isset($api_key_ids[$rid])) {
                $violations[] = "audit event resource api_key missing: {$event->id}";
            } elseif ($type === 'invitation' && !isset($invitation_ids[$rid])) {
                $violations[] = "audit event resource invitation missing: {$event->id}";
            }
        }

        return new ValidationReport(
            ok: empty($violations),
            violations: $violations,
            counts: $counts,
            seed: $seed,
            profile_name: $profile_name,
        );
    }
}
