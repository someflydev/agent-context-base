package tests

import (
	"testing"
	"time"

	"canonical-auth/internal/auth"
	"canonical-auth/internal/domain"

	"github.com/golang-jwt/jwt/v5"
)

func setupTestStore(t *testing.T) *domain.InMemoryStore {
	store, err := domain.LoadFromFixtures("../../domain/fixtures")
	if err != nil {
		t.Fatalf("failed to load fixtures: %v", err)
	}
	return store
}

func TestIssueToken_ClaimsShape(t *testing.T) {
	t.Setenv("TENANTCORE_TEST_SECRET", "test-secret")
	store := setupTestStore(t)
	// alice@acme.example is a tenant_member and is in a group
	user, ok := store.GetUserByEmail("alice@acme.example")
	if !ok {
		t.Fatal("user not found")
	}

	key := []byte("test-secret")
	tokenString, err := auth.IssueToken(user, store, key)
	if err != nil {
		t.Fatalf("failed to issue token: %v", err)
	}

	token, err := jwt.ParseWithClaims(tokenString, &auth.Claims{}, func(token *jwt.Token) (interface{}, error) {
		return key, nil
	}, jwt.WithValidMethods([]string{"HS256"}), jwt.WithIssuer("tenantcore-auth"), jwt.WithAudience("tenantcore-api"))

	if err != nil {
		t.Fatalf("failed to parse token: %v", err)
	}

	claims, ok := token.Claims.(*auth.Claims)
	if !ok || !token.Valid {
		t.Fatal("invalid token claims")
	}

	if claims.Subject != user.ID {
		t.Errorf("expected sub %s, got %s", user.ID, claims.Subject)
	}
	if claims.TenantID == nil {
		t.Error("expected tenant_id not to be nil")
	}
	if claims.TenantRole != "tenant_member" {
		t.Errorf("expected tenant_role tenant_member, got %s", claims.TenantRole)
	}
	if len(claims.Groups) == 0 {
		t.Error("expected groups to be populated")
	}
	if claims.ACLVer != user.ACLVer {
		t.Errorf("expected acl_ver %d, got %d", user.ACLVer, claims.ACLVer)
	}
}

func TestIssueToken_Expiry(t *testing.T) {
	t.Setenv("TENANTCORE_TEST_SECRET", "test-secret")
	store := setupTestStore(t)
	user, _ := store.GetUserByEmail("alice@acme.example")
	key := []byte("test-secret")
	tokenString, err := auth.IssueToken(user, store, key)
	if err != nil {
		t.Fatalf("failed to issue token: %v", err)
	}

	token, _ := jwt.ParseWithClaims(tokenString, &auth.Claims{}, func(token *jwt.Token) (interface{}, error) {
		return key, nil
	}, jwt.WithValidMethods([]string{"HS256"}))

	claims := token.Claims.(*auth.Claims)
	exp := claims.ExpiresAt.Time
	iat := claims.IssuedAt.Time
	diff := exp.Sub(iat)

	if diff != 15*time.Minute {
		t.Errorf("expected 15 min expiry, got %v", diff)
	}
}

func TestIssueToken_Permissions(t *testing.T) {
	t.Setenv("TENANTCORE_TEST_SECRET", "test-secret")
	store := setupTestStore(t)
	user, _ := store.GetUserByEmail("alice@acme.example")
	key := []byte("test-secret")
	tokenString, err := auth.IssueToken(user, store, key)
	if err != nil {
		t.Fatalf("failed to issue token: %v", err)
	}

	token, _ := jwt.ParseWithClaims(tokenString, &auth.Claims{}, func(token *jwt.Token) (interface{}, error) {
		return key, nil
	}, jwt.WithValidMethods([]string{"HS256"}))

	claims := token.Claims.(*auth.Claims)

	effectivePerms := store.GetEffectivePermissions(user.ID)

	if len(claims.Permissions) != len(effectivePerms) {
		t.Errorf("expected %d permissions, got %d", len(effectivePerms), len(claims.Permissions))
	}
}