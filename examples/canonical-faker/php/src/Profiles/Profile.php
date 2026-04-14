<?php
declare(strict_types=1);

namespace AgentContextBase\Faker\Profiles;

final readonly class Profile {
    public const SMOKE = 'smoke';
    public const SMALL = 'small';
    public const MEDIUM = 'medium';
    public const LARGE = 'large';

    public function __construct(
        public string $name,
        public int $numOrgs,
    ) {}

    public static function get(string $name): self {
        return match($name) {
            self::SMOKE => new self(self::SMOKE, 3),
            self::SMALL => new self(self::SMALL, 100),
            self::MEDIUM => new self(self::MEDIUM, 1000),
            self::LARGE => new self(self::LARGE, 10000),
            default => throw new \InvalidArgumentException("Unknown profile: $name"),
        };
    }
}
