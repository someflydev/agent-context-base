package distributions

import (
	"math"
	"math/rand"
)

func WeightedPlan(rng *rand.Rand) string {
	return weightedPick(rng, []string{"free", "pro", "enterprise"}, []int{50, 35, 15})
}

func WeightedRegion(rng *rand.Rand) string {
	return weightedPick(rng, []string{"us-east", "us-west", "eu-west", "ap-southeast"}, []int{40, 25, 20, 15})
}

func WeightedLocale(rng *rand.Rand) string {
	return weightedPick(rng, []string{"en-US", "en-GB", "de-DE", "fr-FR"}, []int{60, 20, 10, 10})
}

func WeightedMembershipRole(rng *rand.Rand) string {
	return weightedPick(rng, []string{"owner", "admin", "member", "viewer"}, []int{5, 10, 60, 25})
}

func WeightedProjectStatus(rng *rand.Rand) string {
	return weightedPick(rng, []string{"active", "archived", "draft"}, []int{60, 25, 15})
}

func WeightedAuditAction(rng *rand.Rand) string {
	return weightedPick(rng, []string{"updated", "created", "exported", "invited", "archived", "deleted"}, []int{35, 20, 15, 12, 10, 8})
}

func WeightedInvitationRole(rng *rand.Rand) string {
	return weightedPick(rng, []string{"admin", "member", "viewer"}, []int{15, 65, 20})
}

func MemberCount(rng *rand.Rand, maxUsers int) int {
	return clamp(int(math.Round(rng.NormFloat64()*2+6)), 3, min(50, maxUsers))
}

func ProjectCount(rng *rand.Rand) int {
	return clamp(int(math.Round(rng.NormFloat64()*2.2+3.5)), 1, 20)
}

func APIKeyCount(rng *rand.Rand) int {
	return clamp(int(math.Round(rng.NormFloat64()*2+2)), 0, 10)
}

func InvitationCount(rng *rand.Rand) int {
	return clamp(int(math.Round(rng.NormFloat64()*1.2+1.5)), 0, 5)
}

func AuditEventCount(rng *rand.Rand, status string) int {
	switch status {
	case "active":
		return clamp(int(math.Round(rng.NormFloat64()*5+14)), 8, 30)
	case "archived":
		return clamp(int(math.Round(rng.NormFloat64()*3+8)), 4, 18)
	default:
		return clamp(int(math.Round(rng.NormFloat64()*2+4)), 2, 10)
	}
}

func weightedPick(rng *rand.Rand, values []string, weights []int) string {
	total := 0
	for _, weight := range weights {
		total += weight
	}
	target := rng.Intn(total)
	running := 0
	for index, value := range values {
		running += weights[index]
		if target < running {
			return value
		}
	}
	return values[len(values)-1]
}

func clamp(value int, minimum int, maximum int) int {
	if value < minimum {
		return minimum
	}
	if value > maximum {
		return maximum
	}
	return value
}

func min(left int, right int) int {
	if left < right {
		return left
	}
	return right
}
