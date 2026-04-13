package pools

import (
	"encoding/csv"
	"encoding/json"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/agent-context-base/canonical-faker-go/internal/domain"
)

var BaseTime = time.Date(2026, time.January, 1, 12, 0, 0, 0, time.UTC)

var TimezoneByLocale = map[string]string{
	"en-US": "America/New_York",
	"en-GB": "Europe/London",
	"de-DE": "Europe/Berlin",
	"fr-FR": "Europe/Paris",
}

type GraphPools struct {
	OrgMemberMap        map[string][]string
	UserEmailByID       map[string]string
	ProjectsByOrg       map[string][]domain.Project
	ProjectByID         map[string]domain.Project
	MembershipsByOrg    map[string][]domain.Membership
	MembershipByOrgUser map[string]domain.Membership
	APIKeysByOrg        map[string][]domain.APIKey
	InvitationsByOrg    map[string][]domain.Invitation
}

func ISO(t time.Time) string {
	return t.UTC().Format(time.RFC3339)
}

func ParseISO(value string) time.Time {
	parsed, _ := time.Parse(time.RFC3339, value)
	return parsed
}

func Slugify(value string) string {
	var builder strings.Builder
	lastDash := false
	for _, r := range strings.ToLower(value) {
		if (r >= 'a' && r <= 'z') || (r >= '0' && r <= '9') {
			builder.WriteRune(r)
			lastDash = false
			continue
		}
		if !lastDash {
			builder.WriteRune('-')
			lastDash = true
		}
	}
	slug := strings.Trim(builder.String(), "-")
	if slug == "" {
		return "tenantcore"
	}
	return slug
}

func Build(dataset domain.Dataset) GraphPools {
	pools := GraphPools{
		OrgMemberMap:        map[string][]string{},
		UserEmailByID:       map[string]string{},
		ProjectsByOrg:       map[string][]domain.Project{},
		ProjectByID:         map[string]domain.Project{},
		MembershipsByOrg:    map[string][]domain.Membership{},
		MembershipByOrgUser: map[string]domain.Membership{},
		APIKeysByOrg:        map[string][]domain.APIKey{},
		InvitationsByOrg:    map[string][]domain.Invitation{},
	}
	for _, user := range dataset.Users {
		pools.UserEmailByID[user.ID] = strings.ToLower(user.Email)
	}
	for _, membership := range dataset.Memberships {
		pools.OrgMemberMap[membership.OrgID] = append(pools.OrgMemberMap[membership.OrgID], membership.UserID)
		pools.MembershipsByOrg[membership.OrgID] = append(pools.MembershipsByOrg[membership.OrgID], membership)
		pools.MembershipByOrgUser[membership.OrgID+":"+membership.UserID] = membership
	}
	for _, project := range dataset.Projects {
		pools.ProjectsByOrg[project.OrgID] = append(pools.ProjectsByOrg[project.OrgID], project)
		pools.ProjectByID[project.ID] = project
	}
	for _, key := range dataset.APIKeys {
		pools.APIKeysByOrg[key.OrgID] = append(pools.APIKeysByOrg[key.OrgID], key)
	}
	for _, invite := range dataset.Invitations {
		pools.InvitationsByOrg[invite.OrgID] = append(pools.InvitationsByOrg[invite.OrgID], invite)
	}
	return pools
}

func WriteJSONL(dataset domain.Dataset, outputDir string, report any) error {
	if err := os.MkdirAll(outputDir, 0o755); err != nil {
		return err
	}
	type entity struct {
		name string
		rows any
	}
	entities := []entity{
		{name: "organizations", rows: dataset.Organizations},
		{name: "users", rows: dataset.Users},
		{name: "memberships", rows: dataset.Memberships},
		{name: "projects", rows: dataset.Projects},
		{name: "audit_events", rows: dataset.AuditEvents},
		{name: "api_keys", rows: dataset.APIKeys},
		{name: "invitations", rows: dataset.Invitations},
	}
	for _, item := range entities {
		path := filepath.Join(outputDir, item.name+".jsonl")
		handle, err := os.Create(path)
		if err != nil {
			return err
		}
		encoder := json.NewEncoder(handle)
		switch rows := item.rows.(type) {
		case []domain.Organization:
			for _, row := range rows {
				if err := encoder.Encode(row); err != nil {
					_ = handle.Close()
					return err
				}
			}
		case []domain.User:
			for _, row := range rows {
				if err := encoder.Encode(row); err != nil {
					_ = handle.Close()
					return err
				}
			}
		case []domain.Membership:
			for _, row := range rows {
				if err := encoder.Encode(row); err != nil {
					_ = handle.Close()
					return err
				}
			}
		case []domain.Project:
			for _, row := range rows {
				if err := encoder.Encode(row); err != nil {
					_ = handle.Close()
					return err
				}
			}
		case []domain.AuditEvent:
			for _, row := range rows {
				if err := encoder.Encode(row); err != nil {
					_ = handle.Close()
					return err
				}
			}
		case []domain.APIKey:
			for _, row := range rows {
				if err := encoder.Encode(row); err != nil {
					_ = handle.Close()
					return err
				}
			}
		case []domain.Invitation:
			for _, row := range rows {
				if err := encoder.Encode(row); err != nil {
					_ = handle.Close()
					return err
				}
			}
		}
		if err := handle.Close(); err != nil {
			return err
		}
	}
	payload, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(outputDir, dataset.ProfileName+"-report.json"), payload, 0o644)
}

func WriteCSV(dataset domain.Dataset, outputDir string, reportCounts map[string]int, reportOK bool, seed int, profile string) error {
	if err := os.MkdirAll(outputDir, 0o755); err != nil {
		return err
	}
	writeReport := func() error {
		handle, err := os.Create(filepath.Join(outputDir, profile+"-report.csv"))
		if err != nil {
			return err
		}
		writer := csv.NewWriter(handle)
		if err := writer.Write([]string{"profile", "seed", "ok", "entity", "count"}); err != nil {
			_ = handle.Close()
			return err
		}
		for entity, count := range reportCounts {
			if err := writer.Write([]string{profile, intToString(seed), boolToString(reportOK), entity, intToString(count)}); err != nil {
				_ = handle.Close()
				return err
			}
		}
		writer.Flush()
		if err := writer.Error(); err != nil {
			_ = handle.Close()
			return err
		}
		return handle.Close()
	}
	return writeReport()
}

func intToString(value int) string {
	return strconv.Itoa(value)
}

func boolToString(value bool) string {
	if value {
		return "true"
	}
	return "false"
}
