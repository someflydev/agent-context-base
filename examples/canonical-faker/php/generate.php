#!/usr/bin/env php
<?php
require __DIR__ . '/vendor/autoload.php';

use AgentContextBase\Faker\Pipeline\TenantCorePipeline;
use AgentContextBase\Faker\Profiles\Profile;
use AgentContextBase\Faker\Validate\Validator;
use Nelmio\Alice\Loader\NativeLoader;

$options = getopt('', ['pipeline:', 'profile:', 'output:', 'format:']);
$pipelineType = $options['pipeline'] ?? 'imperative';
$profileName = $options['profile'] ?? 'smoke';
$outputDir = $options['output'] ?? './output';
$format = $options['format'] ?? 'jsonl';

if ($pipelineType === 'alice' && $profileName !== 'smoke') {
    echo "Note: Alice pipeline only supports the smoke profile in this example.\n";
    exit(1);
}

$profile = Profile::get($profileName);

if ($pipelineType === 'alice') {
    $loader = new NativeLoader();
    $files = [
        __DIR__ . '/alice/organizations.yaml',
        __DIR__ . '/alice/users.yaml',
        __DIR__ . '/alice/memberships.yaml',
    ];
    $objectSet = $loader->loadFileSet($files);
    $objects = $objectSet->getObjects();
    
    $dataset = new \AgentContextBase\Faker\Domain\Dataset(
        organizations: array_values(array_filter($objects, fn($o) => $o instanceof \AgentContextBase\Faker\Domain\Organization)),
        users: array_values(array_filter($objects, fn($o) => $o instanceof \AgentContextBase\Faker\Domain\User)),
        memberships: array_values(array_filter($objects, fn($o) => $o instanceof \AgentContextBase\Faker\Domain\Membership)),
        projects: [],
        audit_events: [],
        api_keys: [],
        invitations: []
    );
} else {
    $pipeline = new TenantCorePipeline($profile);
    $dataset = $pipeline->generate();
}

$report = Validator::check($dataset, 42, $profileName);

if (!is_dir($outputDir)) {
    mkdir($outputDir, 0777, true);
}

$entities = [
    'organizations' => $dataset->organizations,
    'users' => $dataset->users,
    'memberships' => $dataset->memberships,
    'projects' => $dataset->projects,
    'audit_events' => $dataset->audit_events,
    'api_keys' => $dataset->api_keys,
    'invitations' => $dataset->invitations,
];

foreach ($entities as $entityName => $items) {
    if ($format === 'jsonl') {
        $file = fopen("$outputDir/$entityName.jsonl", 'w');
        foreach ($items as $item) {
            fwrite($file, json_encode($item->toArray()) . "\n");
        }
        fclose($file);
    } else {
        $file = fopen("$outputDir/$entityName.csv", 'w');
        if (!empty($items)) {
            $first = true;
            foreach ($items as $item) {
                $row = $item->toArray();
                if ($first) {
                    fputcsv($file, array_keys($row));
                    $first = false;
                }
                fputcsv($file, array_values($row));
            }
        }
        fclose($file);
    }
}

if (!$report->ok) {
    if ($pipelineType !== 'alice') {
        echo "Validation failed!\n";
        foreach ($report->violations as $v) {
            echo "- $v\n";
        }
        exit(1);
    } else {
        echo "Validation failed! (Expected for Alice due to temporal limitations)\n";
        foreach ($report->violations as $v) {
            echo "- $v\n";
        }
    }
}

echo "Dataset generated successfully.\n";
