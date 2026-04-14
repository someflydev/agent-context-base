<?php
declare(strict_types=1);

namespace AgentContextBase\Faker\Distributions;

final class Distributions {
    public static function weightedChoice(array $weights, \Random\Randomizer $rng): string {
        $totalWeight = array_sum($weights);
        if ($totalWeight === 0) {
            return (string)array_key_first($weights);
        }
        $target = $rng->getInt(1, $totalWeight);
        
        $cumulative = 0;
        foreach ($weights as $value => $weight) {
            $cumulative += $weight;
            if ($target <= $cumulative) {
                return (string)$value;
            }
        }
        return (string)array_key_first($weights);
    }
}
