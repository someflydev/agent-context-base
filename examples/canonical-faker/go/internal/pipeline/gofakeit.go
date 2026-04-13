package pipeline

import (
	"fmt"
	"math/rand"
	"sort"
	"strings"
	"time"

	"github.com/agent-context-base/canonical-faker-go/internal/distributions"
	"github.com/agent-context-base/canonical-faker-go/internal/domain"
	"github.com/agent-context-base/canonical-faker-go/internal/pools"
	"github.com/agent-context-base/canonical-faker-go/internal/profiles"
	"github.com/brianvoe/gofakeit/v6"
)

const invitationExpiryWindowDays = 30

func GenerateWithGoFakeIt(profile profiles.Profile) (domain.Dataset, error) {
	fake := gofakeit.New(int64(profile.Seed))
	// The RNG that shapes weighted distributions is seeded separately but with
	// the same seed value. Go does not provide a single globally-seeded faker.
	rng := rand.New(rand.NewSource(int64(profile.Seed)))

	organizations := make([]domain.Organization, 0, profile.NumOrgs)
	users := make([]domain.User, 0, profile.NumUsers)
	memberships := []domain.Membership{}
	projects := []domain.Project{}
	apiKeys := []domain.APIKey{}
	invitations := []domain.Invitation{}
	auditEvents := []domain.AuditEvent{}

	seenSlugs := map[string]bool{}
	seenOrgEmails := map[string]bool{}
	seenUserEmails := map[string]bool{}
	seenPrefixes := map[string]bool{}

	for i := 0; i < profile.NumOrgs; i++ {
		name := fake.Company()
		baseSlug := pools.Slugify(name)
		slug := baseSlug
		for suffix := 2; seenSlugs[slug]; suffix++ {
			slug = fmt.Sprintf("%s-%d", baseSlug, suffix)
		}
		seenSlugs[slug] = true
		email := strings.ToLower(fake.Email())
		for seenOrgEmails[email] {
			email = strings.ToLower(fake.Email())
		}
		seenOrgEmails[email] = true
		organizations = append(organizations, domain.Organization{
			ID:         fake.UUID(),
			Name:       name,
			Slug:       slug,
			Plan:       distributions.WeightedPlan(rng),
			Region:     distributions.WeightedRegion(rng),
			CreatedAt:  pools.ISO(fake.DateRange(pools.BaseTime.AddDate(-3, 0, 0), pools.BaseTime)),
			OwnerEmail: email,
		})
	}

	edgeNames := []string{"Sofie D'Aubigne", "Bjorn Asmussen", "Francois L'Ecuyer", "Marta Nunez de la Pena", "Zoe Kruger-Renaud"}
	for i := 0; i < profile.NumUsers; i++ {
		locale := distributions.WeightedLocale(rng)
		email := strings.ToLower(fake.Email())
		edgeCase := rng.Float64() < 0.05
		if edgeCase {
			email = fmt.Sprintf("edgecase%03d.%s@tenantcore-example.test", i, strings.ToLower(strings.ReplaceAll(locale, "-", "")))
		}
		for seenUserEmails[email] {
			email = strings.ToLower(fake.Email())
		}
		seenUserEmails[email] = true
		name := fake.Name()
		if edgeCase {
			name = edgeNames[i%len(edgeNames)]
		}
		users = append(users, domain.User{
			ID:        fake.UUID(),
			Email:     email,
			FullName:  name,
			Locale:    locale,
			Timezone:  pools.TimezoneByLocale[locale],
			CreatedAt: pools.ISO(fake.DateRange(pools.BaseTime.AddDate(-3, 0, 0), pools.BaseTime)),
		})
	}

	for _, organization := range organizations {
		memberRows := sampleUsers(users, distributions.MemberCount(rng, len(users)), rng)
		for index, user := range memberRows {
			var invitedBy *string
			if index > 0 {
				id := memberRows[rng.Intn(index)].ID
				invitedBy = &id
			}
			memberships = append(memberships, domain.Membership{
				ID:        fake.UUID(),
				OrgID:     organization.ID,
				UserID:    user.ID,
				Role:      pickRole(index, rng),
				JoinedAt:  pools.ISO(fake.DateRange(pools.ParseISO(organization.CreatedAt), pools.BaseTime)),
				InvitedBy: invitedBy,
			})
		}
	}

	baseDataset := domain.Dataset{ProfileName: profile.Name, Seed: profile.Seed, Organizations: organizations, Users: users, Memberships: memberships}
	graph := pools.Build(baseDataset)

	for _, organization := range organizations {
		memberIDs := graph.OrgMemberMap[organization.ID]
		for i := 0; i < distributions.ProjectCount(rng); i++ {
			projects = append(projects, domain.Project{
				ID:        fake.UUID(),
				OrgID:     organization.ID,
				Name:      fake.ProductName(),
				Status:    distributions.WeightedProjectStatus(rng),
				CreatedBy: memberIDs[rng.Intn(len(memberIDs))],
				CreatedAt: pools.ISO(fake.DateRange(pools.ParseISO(organization.CreatedAt), pools.BaseTime)),
			})
		}
	}

	graph = pools.Build(domain.Dataset{ProfileName: profile.Name, Seed: profile.Seed, Organizations: organizations, Users: users, Memberships: memberships, Projects: projects})
	for _, organization := range organizations {
		memberIDs := graph.OrgMemberMap[organization.ID]
		memberEmails := map[string]bool{}
		for _, memberID := range memberIDs {
			memberEmails[graph.UserEmailByID[memberID]] = true
		}
		for i := 0; i < distributions.APIKeyCount(rng); i++ {
			keyPrefix := "tc_" + randomKey(rng)
			for seenPrefixes[keyPrefix] {
				keyPrefix = "tc_" + randomKey(rng)
			}
			seenPrefixes[keyPrefix] = true
			createdAt := fake.DateRange(pools.ParseISO(organization.CreatedAt), pools.BaseTime)
			var lastUsedAt *string
			if rng.Float64() < 0.70 {
				value := pools.ISO(fake.DateRange(createdAt, pools.BaseTime))
				lastUsedAt = &value
			}
			apiKeys = append(apiKeys, domain.APIKey{
				ID:         fake.UUID(),
				OrgID:      organization.ID,
				CreatedBy:  memberIDs[rng.Intn(len(memberIDs))],
				Name:       fake.BuzzWord(),
				KeyPrefix:  keyPrefix,
				CreatedAt:  pools.ISO(createdAt),
				LastUsedAt: lastUsedAt,
			})
		}
		for i := 0; i < distributions.InvitationCount(rng); i++ {
			email := strings.ToLower(fake.Email())
			for memberEmails[email] {
				email = strings.ToLower(fake.Email())
			}
			var acceptedAt *string
			if rng.Float64() < 0.40 {
				value := pools.ISO(pools.BaseTime.Add(-time.Duration(rng.Intn(180)+1) * 24 * time.Hour))
				acceptedAt = &value
			}
			expiresAt := pools.BaseTime.Add(time.Duration(rng.Intn(invitationExpiryWindowDays)+1) * 24 * time.Hour)
			invitations = append(invitations, domain.Invitation{
				ID:           fake.UUID(),
				OrgID:        organization.ID,
				InvitedEmail: email,
				Role:         distributions.WeightedInvitationRole(rng),
				InvitedBy:    memberIDs[rng.Intn(len(memberIDs))],
				ExpiresAt:    pools.ISO(expiresAt),
				AcceptedAt:   acceptedAt,
			})
		}
	}

	graph = pools.Build(domain.Dataset{ProfileName: profile.Name, Seed: profile.Seed, Organizations: organizations, Users: users, Memberships: memberships, Projects: projects, APIKeys: apiKeys, Invitations: invitations})
	for _, project := range projects {
		memberIDs := graph.OrgMemberMap[project.OrgID]
		projectMemberships := graph.MembershipsByOrg[project.OrgID]
		orgAPIKeys := graph.APIKeysByOrg[project.OrgID]
		orgInvitations := graph.InvitationsByOrg[project.OrgID]
		for i := 0; i < distributions.AuditEventCount(rng, project.Status); i++ {
			userID := memberIDs[rng.Intn(len(memberIDs))]
			membership := graph.MembershipByOrgUser[project.OrgID+":"+userID]
			floor := maxTime(pools.ParseISO(project.CreatedAt), pools.ParseISO(membership.JoinedAt))
			resourceType := weightedResourceType(rng)
			resourceID := project.ID
			switch resourceType {
			case "user":
				resourceID = userID
			case "membership":
				resourceID = projectMemberships[rng.Intn(len(projectMemberships))].ID
			case "api_key":
				if len(orgAPIKeys) > 0 {
					resourceID = orgAPIKeys[rng.Intn(len(orgAPIKeys))].ID
				} else {
					resourceType = "project"
				}
			case "invitation":
				if len(orgInvitations) > 0 {
					resourceID = orgInvitations[rng.Intn(len(orgInvitations))].ID
				} else {
					resourceType = "project"
				}
			}
			auditEvents = append(auditEvents, domain.AuditEvent{
				ID:           fake.UUID(),
				OrgID:        project.OrgID,
				UserID:       userID,
				ProjectID:    project.ID,
				Action:       distributions.WeightedAuditAction(rng),
				ResourceType: resourceType,
				ResourceID:   resourceID,
				TS:           pools.ISO(fake.DateRange(floor, pools.BaseTime)),
			})
		}
	}

	sort.Slice(auditEvents, func(i int, j int) bool {
		return auditEvents[i].TS < auditEvents[j].TS
	})

	return domain.Dataset{
		ProfileName:   profile.Name,
		Seed:          profile.Seed,
		Organizations: organizations,
		Users:         users,
		Memberships:   memberships,
		Projects:      projects,
		AuditEvents:   auditEvents,
		APIKeys:       apiKeys,
		Invitations:   invitations,
	}, nil
}

func sampleUsers(users []domain.User, count int, rng *rand.Rand) []domain.User {
	indices := rng.Perm(len(users))[:count]
	rows := make([]domain.User, 0, count)
	for _, index := range indices {
		rows = append(rows, users[index])
	}
	return rows
}

func pickRole(index int, rng *rand.Rand) string {
	if index == 0 {
		return "owner"
	}
	return distributions.WeightedMembershipRole(rng)
}

func randomKey(rng *rand.Rand) string {
	const alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
	chars := make([]byte, 8)
	for i := range chars {
		chars[i] = alphabet[rng.Intn(len(alphabet))]
	}
	return string(chars)
}

func weightedResourceType(rng *rand.Rand) string {
	values := []string{"project", "user", "membership", "api_key", "invitation"}
	weights := []int{35, 15, 25, 10, 15}
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
	return "project"
}

func maxTime(left time.Time, right time.Time) time.Time {
	if left.After(right) {
		return left
	}
	return right
}
