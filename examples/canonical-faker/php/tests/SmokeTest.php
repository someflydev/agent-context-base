<?php
declare(strict_types=1);

namespace AgentContextBase\Faker\Tests;

use PHPUnit\Framework\TestCase;
use AgentContextBase\Faker\Pipeline\TenantCorePipeline;
use AgentContextBase\Faker\Profiles\Profile;
use AgentContextBase\Faker\Validate\Validator;

class SmokeTest extends TestCase
{
    public function testGeneratesCorrectOrgCount(): void
    {
        $pipeline = new TenantCorePipeline(Profile::get(Profile::SMOKE));
        $dataset = $pipeline->generate();
        $this->assertCount(3, $dataset->organizations);
    }

    public function testPassesValidation(): void
    {
        $pipeline = new TenantCorePipeline(Profile::get(Profile::SMOKE));
        $dataset = $pipeline->generate();
        $report = Validator::check($dataset, 42, 'smoke');
        $this->assertTrue($report->ok, implode("\n", $report->violations));
    }

    public function testIsReproducible(): void
    {
        $d1 = (new TenantCorePipeline(Profile::get(Profile::SMOKE)))->generate();
        $d2 = (new TenantCorePipeline(Profile::get(Profile::SMOKE)))->generate();
        $this->assertEquals($d1->organizations, $d2->organizations);
    }
}
