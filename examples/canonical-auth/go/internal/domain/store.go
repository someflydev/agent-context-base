package domain

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

type InMemoryStore struct {
	Users           []User
	Tenants         []Tenant
	Memberships     []Membership
	Groups          []Group
	Permissions     []Permission
	GroupPermissions []GroupPermission
	UserGroups      []UserGroup
}

func (s *InMemoryStore) GetUserByID(id string) (*User, bool) {
	for _, u := range s.Users {
		if u.ID == id {
			return &u, true
		}
	}
	return nil, false
}

func (s *InMemoryStore) GetUserByEmail(email string) (*User, bool) {
	for _, u := range s.Users {
		if u.Email == email {
			return &u, true
		}
	}
	return nil, false
}

func (s *InMemoryStore) GetTenantByID(id string) (*Tenant, bool) {
	for _, t := range s.Tenants {
		if t.ID == id {
			return &t, true
		}
	}
	return nil, false
}

func (s *InMemoryStore) GetMembership(userID string) (*Membership, bool) {
	for _, m := range s.Memberships {
		if m.UserID == userID && m.IsActive {
			return &m, true
		}
	}
	return nil, false
}

func (s *InMemoryStore) GetGroupsForUser(userID, tenantID string) []Group {
	var userGroupIDs []string
	for _, ug := range s.UserGroups {
		if ug.UserID == userID {
			userGroupIDs = append(userGroupIDs, ug.GroupID)
		}
	}

	var groups []Group
	for _, g := range s.Groups {
		if g.TenantID == tenantID {
			for _, ugID := range userGroupIDs {
				if g.ID == ugID {
					groups = append(groups, g)
					break
				}
			}
		}
	}
	return groups
}

func (s *InMemoryStore) GetEffectivePermissions(userID string) []string {
	var userGroupIDs []string
	for _, ug := range s.UserGroups {
		if ug.UserID == userID {
			userGroupIDs = append(userGroupIDs, ug.GroupID)
		}
	}

	var groupIDs []string
	for _, g := range s.Groups {
		for _, ugID := range userGroupIDs {
			if g.ID == ugID {
				groupIDs = append(groupIDs, g.ID)
				break
			}
		}
	}

	var permIDs []string
	for _, gp := range s.GroupPermissions {
		for _, gID := range groupIDs {
			if gp.GroupID == gID {
				permIDs = append(permIDs, gp.PermissionID)
				break
			}
		}
	}

	permMap := make(map[string]bool)
	for _, p := range s.Permissions {
		for _, pID := range permIDs {
			if p.ID == pID {
				permMap[p.Name] = true
				break
			}
		}
	}

	var perms []string
	for p := range permMap {
		perms = append(perms, p)
	}
	return perms
}

func (s *InMemoryStore) VerifyMembership(userID, tenantID string) bool {
	for _, m := range s.Memberships {
		if m.UserID == userID && m.IsActive {
			if m.TenantID != nil && *m.TenantID == tenantID {
				return true
			}
		}
	}
	return false
}

func (s *InMemoryStore) GetTenantName(tenantID string) string {
	if t, ok := s.GetTenantByID(tenantID); ok {
		return t.Name
	}
	return ""
}

func LoadFromFixtures(fixtureDir string) (*InMemoryStore, error) {
	if fixtureDir == "" {
		fixtureDir = "../../domain/fixtures"
	}

	store := &InMemoryStore{}

	if err := loadJSON(filepath.Join(fixtureDir, "users.json"), &store.Users); err != nil {
		return nil, err
	}
	if err := loadJSON(filepath.Join(fixtureDir, "tenants.json"), &store.Tenants); err != nil {
		return nil, err
	}
	if err := loadJSON(filepath.Join(fixtureDir, "memberships.json"), &store.Memberships); err != nil {
		return nil, err
	}
	if err := loadJSON(filepath.Join(fixtureDir, "groups.json"), &store.Groups); err != nil {
		return nil, err
	}
	if err := loadJSON(filepath.Join(fixtureDir, "permissions.json"), &store.Permissions); err != nil {
		return nil, err
	}
	if err := loadJSON(filepath.Join(fixtureDir, "group_permissions.json"), &store.GroupPermissions); err != nil {
		return nil, err
	}
	if err := loadJSON(filepath.Join(fixtureDir, "user_groups.json"), &store.UserGroups); err != nil {
		return nil, err
	}

	return store, nil
}

func loadJSON(path string, v interface{}) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("failed to read fixture %s: %w", path, err)
	}
	if err := json.Unmarshal(data, v); err != nil {
		return fmt.Errorf("failed to parse fixture %s: %w", path, err)
	}
	return nil
}
