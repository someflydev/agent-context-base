<?php
declare(strict_types=1);

namespace AgentContextBase\Faker\Pools;

final class IdPools {
    /** @var string[] */
    public array $orgIds = [];
    
    /** @var string[] */
    public array $userIds = [];
    
    /** @var array<string, array<string, string>> */
    public array $orgMembers = [];
    
    /** @var array<string, string[]> */
    public array $projectIds = [];
    
    /** @var array<string, string[]> */
    public array $memberEmails = [];
}
