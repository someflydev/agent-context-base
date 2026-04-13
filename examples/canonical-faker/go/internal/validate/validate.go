package validate

import (
	"fmt"
	"strings"
	"time"

	"github.com/agent-context-base/canonical-faker-go/internal/domain"
	"github.com/agent-context-base/canonical-faker-go/internal/pools"
)

type ValidationReport struct {
	OK         bool           `json:"ok"`
	Violations []string       `json:"violations"`
	Counts     map[string]int `json:"counts"`
	Seed       int            `json:"seed"`
	Profile    string         `json:"profile"`
}

func Dataset(dataset domain.Dataset) ValidationReport {
	violations := []string{}
	counts := map[string]int{
		"organizations": len(dataset.Organizations),
		"users":         len(dataset.Users),
		"memberships":   len(dataset.Memberships),
		"projects":      len(dataset.Projects),
		"audit_events":  len(dataset.AuditEvents),
		"api_keys":      len(dataset.APIKeys),
		"invitations":   len(dataset.Invitations),
	}
	minimumRows := map[string]int{
		"organizations": 1,
		"users":         1,
		"memberships":   1,
		"projects":      1,
		"audit_events":  1,
		"api_keys":      0,
		"invitations":   0,
	}
	for entity, count := range counts {
		if count < minimumRows[entity] {
			violations = append(violations, fmt.Sprintf("row count below minimum for %s: %d < %d", entity, count, minimumRows[entity]))
		}
	}
	orgs := map[string]domain.Organization{}
	users := map[string]domain.User{}
	memberEmails := map[string]map[string]bool{}
	seenOrgIDs := map[string]bool{}
	seenEmails := map[string]bool{}
	seenPrefixes := map[string]bool{}

	for _, org := range dataset.Organizations {
		if seenOrgIDs[org.ID] {
			violations = append(violations, "duplicate organizations.id: "+org.ID)
		}
		seenOrgIDs[org.ID] = true
		orgs[org.ID] = org
	}
	for _, user := range dataset.Users {
		email := strings.ToLower(user.Email)
		if seenEmails[email] {
			violations = append(violations, "duplicate user.email: "+email)
		}
		seenEmails[email] = true
		users[user.ID] = user
	}
	graph := pools.Build(dataset)
	projects := map[string]domain.Project{}
	for _, project := range dataset.Projects {
		projects[project.ID] = project
	}
	membershipIDs := map[string]bool{}
	for _, membership := range dataset.Memberships {
		org, hasOrg := orgs[membership.OrgID]
		user, hasUser := users[membership.UserID]
		if !hasOrg {
			violations = append(violations, "membership missing org: "+membership.ID)
			continue
		}
		if !hasUser {
			violations = append(violations, "membership missing user: "+membership.ID)
			continue
		}
		membershipIDs[membership.ID] = true
		if memberEmails[membership.OrgID] == nil {
			memberEmails[membership.OrgID] = map[string]bool{}
		}
		memberEmails[membership.OrgID][strings.ToLower(user.Email)] = true
		if pools.ParseISO(membership.JoinedAt).Before(pools.ParseISO(org.CreatedAt)) {
			violations = append(violations, "Rule A violated by membership "+membership.ID)
		}
		if membership.InvitedBy != nil {
			if _, ok := users[*membership.InvitedBy]; !ok {
				violations = append(violations, "membership invited_by missing user: "+membership.ID)
			}
		}
	}
	apiKeyIDs := map[string]bool{}
	for _, key := range dataset.APIKeys {
		apiKeyIDs[key.ID] = true
		if !contains(graph.OrgMemberMap[key.OrgID], key.CreatedBy) {
			violations = append(violations, "Rule G violated by api_key "+key.ID)
		}
		if seenPrefixes[key.KeyPrefix] {
			violations = append(violations, "duplicate api_key.key_prefix: "+key.KeyPrefix)
		}
		seenPrefixes[key.KeyPrefix] = true
		if key.LastUsedAt != nil && pools.ParseISO(*key.LastUsedAt).Before(pools.ParseISO(key.CreatedAt)) {
			violations = append(violations, "api_key last_used_at before created_at: "+key.ID)
		}
	}
	invitationIDs := map[string]bool{}
	for _, invitation := range dataset.Invitations {
		invitationIDs[invitation.ID] = true
		if !contains(graph.OrgMemberMap[invitation.OrgID], invitation.InvitedBy) {
			violations = append(violations, "Rule H violated by invitation "+invitation.ID)
		}
		if memberEmails[invitation.OrgID][strings.ToLower(invitation.InvitedEmail)] {
			violations = append(violations, "Rule I violated by invitation "+invitation.ID)
		}
		expiresAt := pools.ParseISO(invitation.ExpiresAt)
		if !expiresAt.After(pools.BaseTime) {
			violations = append(violations, "invitation expiry must be in the future: "+invitation.ID)
		}
		if expiresAt.After(pools.BaseTime.Add(30 * 24 * time.Hour)) {
			violations = append(violations, "invitation expiry must be within 30 days: "+invitation.ID)
		}
		if invitation.AcceptedAt != nil && pools.ParseISO(*invitation.AcceptedAt).After(pools.BaseTime) {
			violations = append(violations, "invitation accepted_at must be in the past: "+invitation.ID)
		}
	}
	for _, project := range dataset.Projects {
		org, ok := orgs[project.OrgID]
		if !ok {
			violations = append(violations, "project missing org: "+project.ID)
			continue
		}
		if pools.ParseISO(project.CreatedAt).Before(pools.ParseISO(org.CreatedAt)) {
			violations = append(violations, "Rule B violated by project "+project.ID)
		}
		if !contains(graph.OrgMemberMap[project.OrgID], project.CreatedBy) {
			violations = append(violations, "Rule C violated by project "+project.ID)
		}
	}
	for _, event := range dataset.AuditEvents {
		project, ok := projects[event.ProjectID]
		if !ok {
			violations = append(violations, "audit event missing project: "+event.ID)
			continue
		}
		if _, hasOrg := orgs[event.OrgID]; !hasOrg {
			violations = append(violations, "audit event missing org: "+event.ID)
			continue
		}
		if !contains(graph.OrgMemberMap[event.OrgID], event.UserID) {
			violations = append(violations, "Rule D violated by audit event "+event.ID)
		}
		if project.OrgID != event.OrgID {
			violations = append(violations, "Rule E violated by audit event "+event.ID)
		}
		if pools.ParseISO(event.TS).Before(pools.ParseISO(project.CreatedAt)) {
			violations = append(violations, "Rule F violated by audit event "+event.ID)
		}
		membership := graph.MembershipByOrgUser[event.OrgID+":"+event.UserID]
		if !membershipIsZero(membership) && pools.ParseISO(event.TS).Before(pools.ParseISO(membership.JoinedAt)) {
			violations = append(violations, "audit event before membership joined_at: "+event.ID)
		}
		switch event.ResourceType {
		case "project":
			if _, ok := projects[event.ResourceID]; !ok {
				violations = append(violations, "audit event resource project missing: "+event.ID)
			}
		case "user":
			if _, ok := users[event.ResourceID]; !ok {
				violations = append(violations, "audit event resource user missing: "+event.ID)
			}
		case "membership":
			if !membershipIDs[event.ResourceID] {
				violations = append(violations, "audit event resource membership missing: "+event.ID)
			}
		case "api_key":
			if !apiKeyIDs[event.ResourceID] {
				violations = append(violations, "audit event resource api_key missing: "+event.ID)
			}
		case "invitation":
			if !invitationIDs[event.ResourceID] {
				violations = append(violations, "audit event resource invitation missing: "+event.ID)
			}
		}
	}

	return ValidationReport{
		OK:         len(violations) == 0,
		Violations: violations,
		Counts:     counts,
		Seed:       dataset.Seed,
		Profile:    dataset.ProfileName,
	}
}

func contains(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
}

func membershipIsZero(value domain.Membership) bool {
	return value.ID == ""
}
