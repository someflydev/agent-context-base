package auth

import (
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type Claims struct {
	jwt.RegisteredClaims
	TenantID    *string  `json:"tenant_id"`
	TenantRole  string   `json:"tenant_role"`
	Groups      []string `json:"groups"`
	Permissions []string `json:"permissions"`
	ACLVer      int      `json:"acl_ver"`
}

type AuthContext struct {
	Sub         string
	Email       string
	TenantID    *string
	TenantRole  string
	Groups      []string
	Permissions []string
	ACLVer      int
	IssuedAt    time.Time
	ExpiresAt   time.Time
}

func (a *AuthContext) HasPermission(permission string) bool {
	for _, p := range a.Permissions {
		if p == permission {
			return true
		}
	}
	return false
}
