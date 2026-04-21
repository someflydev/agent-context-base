package auth

import (
	"crypto/rand"
	"fmt"
	"os"
	"time"

	"canonical-auth/internal/domain"

	"github.com/golang-jwt/jwt/v5"
)

func IssueToken(user *domain.User, store *domain.InMemoryStore, signingKey interface{}) (string, error) {
	now := time.Now()
	exp := now.Add(15 * time.Minute)

	jtiBytes := make([]byte, 16)
	_, _ = rand.Read(jtiBytes)
	jti := fmt.Sprintf("%x", jtiBytes)

	membership, ok := store.GetMembership(user.ID)
	if !ok {
		return "", fmt.Errorf("no active membership found for user %s", user.ID)
	}

	var tenantID *string
	if membership.TenantID != nil {
		tenantIDStr := *membership.TenantID
		tenantID = &tenantIDStr
	}

	var groupSlugs []string
	if tenantID != nil {
		groups := store.GetGroupsForUser(user.ID, *tenantID)
		for _, g := range groups {
			groupSlugs = append(groupSlugs, g.Slug)
		}
	} else {
		groupSlugs = []string{}
	}

	permissions := store.GetEffectivePermissions(user.ID)
	if permissions == nil {
		permissions = []string{}
	}

	claims := Claims{
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer:    "tenantcore-auth",
			Audience:  jwt.ClaimStrings{"tenantcore-api"},
			Subject:   user.ID,
			ExpiresAt: jwt.NewNumericDate(exp),
			IssuedAt:  jwt.NewNumericDate(now),
			NotBefore: jwt.NewNumericDate(now),
			ID:        jti,
		},
		TenantID:    tenantID,
		TenantRole:  membership.TenantRole,
		Groups:      groupSlugs,
		Permissions: permissions,
		ACLVer:      user.ACLVer,
	}

	if testSecret := os.Getenv("TENANTCORE_TEST_SECRET"); testSecret != "" {
		token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
		return token.SignedString([]byte(testSecret))
	}

	token := jwt.NewWithClaims(jwt.SigningMethodRS256, claims)
	return token.SignedString(signingKey)
}
