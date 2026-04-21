package tests

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"canonical-auth/internal/auth"
	"canonical-auth/internal/domain"
	"canonical-auth/internal/routes"

	"github.com/golang-jwt/jwt/v5"
	"github.com/labstack/echo/v4"
)

func setupTestApp(t *testing.T) (*echo.Echo, *domain.InMemoryStore, []byte) {
	store := setupTestStore(t)
	key := []byte("test-secret")
	t.Setenv("TENANTCORE_TEST_SECRET", "test-secret")

	e := echo.New()

	authRoutes := &routes.AuthRoutes{
		Store:      store,
		SigningKey: key,
	}
	meRoutes := &routes.MeRoutes{Store: store}
	usersRoutes := &routes.UsersRoutes{Store: store}
	adminRoutes := &routes.AdminRoutes{Store: store}

	e.POST("/auth/token", authRoutes.Token)
	
	protected := e.Group("", auth.JWTMiddleware(store, key))
	protected.GET("/me", meRoutes.Me)
	protected.GET("/users", usersRoutes.List, auth.RequirePermission("iam:user:read"))
	protected.POST("/users", usersRoutes.Invite, auth.RequirePermission("iam:user:invite"))
	protected.GET("/users/:id", usersRoutes.Get, auth.RequirePermission("iam:user:read"))
	protected.GET("/admin/tenants", adminRoutes.ListTenants, auth.RequireSuperAdmin())

	return e, store, key
}

func issueTestToken(t *testing.T, store *domain.InMemoryStore, key []byte, email string) string {
	user, ok := store.GetUserByEmail(email)
	if !ok {
		t.Fatalf("user %s not found", email)
	}
	token, err := auth.IssueToken(user, store, key)
	if err != nil {
		t.Fatalf("failed to issue token: %v", err)
	}
	return token
}

func TestAuth_SmokeTests(t *testing.T) {
	e, store, key := setupTestApp(t)

	// 1. token_issue_success
	t.Run("token_issue_success", func(t *testing.T) {
		reqBody := `{"email": "admin@acme.example", "password": "password123"}`
		req := httptest.NewRequest(http.MethodPost, "/auth/token", bytes.NewBufferString(reqBody))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusOK {
			t.Errorf("expected 200, got %d", rec.Code)
		}
		var resp map[string]string
		if err := json.Unmarshal(rec.Body.Bytes(), &resp); err != nil {
			t.Fatalf("failed to decode response: %v", err)
		}
		if resp["access_token"] == "" {
			t.Error("missing access_token")
		}
	})

	// 2. token_invalid_credentials
	t.Run("token_invalid_credentials", func(t *testing.T) {
		reqBody := `{"email": "admin@acme.example", "password": "wrong"}`
		req := httptest.NewRequest(http.MethodPost, "/auth/token", bytes.NewBufferString(reqBody))
		req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusUnauthorized {
			t.Errorf("expected 401, got %d", rec.Code)
		}
	})

	// 3. token_expired_rejection
	t.Run("token_expired_rejection", func(t *testing.T) {
		user, _ := store.GetUserByEmail("admin@acme.example")
		now := time.Now().Add(-30 * time.Minute)
		exp := now.Add(15 * time.Minute)
		claims := auth.Claims{
			RegisteredClaims: jwt.RegisteredClaims{
				Issuer:    "tenantcore-auth",
				Audience:  jwt.ClaimStrings{"tenantcore-api"},
				Subject:   user.ID,
				ExpiresAt: jwt.NewNumericDate(exp),
				IssuedAt:  jwt.NewNumericDate(now),
			},
			ACLVer: user.ACLVer,
		}
		token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
		expiredTokenStr, _ := token.SignedString(key)

		req := httptest.NewRequest(http.MethodGet, "/me", nil)
		req.Header.Set("Authorization", "Bearer "+expiredTokenStr)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusUnauthorized {
			t.Errorf("expected 401, got %d", rec.Code)
		}
	})

	// 4. token_stale_acl_ver
	t.Run("token_stale_acl_ver", func(t *testing.T) {
		user, _ := store.GetUserByEmail("admin@acme.example")
		now := time.Now()
		exp := now.Add(15 * time.Minute)
		claims := auth.Claims{
			RegisteredClaims: jwt.RegisteredClaims{
				Issuer:    "tenantcore-auth",
				Audience:  jwt.ClaimStrings{"tenantcore-api"},
				Subject:   user.ID,
				ExpiresAt: jwt.NewNumericDate(exp),
			},
			ACLVer: user.ACLVer - 1, // Stale version
		}
		token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
		staleTokenStr, _ := token.SignedString(key)

		req := httptest.NewRequest(http.MethodGet, "/me", nil)
		req.Header.Set("Authorization", "Bearer "+staleTokenStr)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusUnauthorized {
			t.Errorf("expected 401 for stale acl_ver, got %d", rec.Code)
		}
	})

	// 5. get_me_success
	t.Run("get_me_success", func(t *testing.T) {
		token := issueTestToken(t, store, key, "admin@acme.example")
		req := httptest.NewRequest(http.MethodGet, "/me", nil)
		req.Header.Set("Authorization", "Bearer "+token)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusOK {
			t.Errorf("expected 200, got %d", rec.Code)
		}
	})

	// 6. get_me_unauthorized
	t.Run("get_me_unauthorized", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodGet, "/me", nil)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusUnauthorized {
			t.Errorf("expected 401, got %d", rec.Code)
		}
	})

	// 7. rbac_permission_granted
	t.Run("rbac_permission_granted", func(t *testing.T) {
		token := issueTestToken(t, store, key, "alice@acme.example") // has iam:user:read
		req := httptest.NewRequest(http.MethodGet, "/users", nil)
		req.Header.Set("Authorization", "Bearer "+token)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusOK {
			t.Errorf("expected 200, got %d", rec.Code)
		}
	})

	// 8. rbac_permission_denied
	t.Run("rbac_permission_denied", func(t *testing.T) {
		token := issueTestToken(t, store, key, "bob@acme.example") // has no iam:user:invite
		req := httptest.NewRequest(http.MethodPost, "/users", nil)
		req.Header.Set("Authorization", "Bearer "+token)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusForbidden {
			t.Errorf("expected 403, got %d", rec.Code)
		}
	})

	// 9. cross_tenant_denial
	t.Run("cross_tenant_denial", func(t *testing.T) {
		token := issueTestToken(t, store, key, "admin@acme.example") // tenant A
		globexUser, _ := store.GetUserByEmail("carol@globex.example") // tenant B

		req := httptest.NewRequest(http.MethodGet, "/users/"+globexUser.ID, nil)
		req.Header.Set("Authorization", "Bearer "+token)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusForbidden {
			t.Errorf("expected 403 for cross-tenant, got %d", rec.Code)
		}
	})

	// 10. super_admin_access
	t.Run("super_admin_access", func(t *testing.T) {
		token := issueTestToken(t, store, key, "superadmin@tenantcore.dev")
		req := httptest.NewRequest(http.MethodGet, "/admin/tenants", nil)
		req.Header.Set("Authorization", "Bearer "+token)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusOK {
			t.Errorf("expected 200, got %d", rec.Code)
		}
	})

	// 11. super_admin_tenant_scoped_denial
	t.Run("super_admin_tenant_scoped_denial", func(t *testing.T) {
		token := issueTestToken(t, store, key, "superadmin@tenantcore.dev")
		req := httptest.NewRequest(http.MethodGet, "/users", nil)
		req.Header.Set("Authorization", "Bearer "+token)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusForbidden {
			t.Errorf("expected 403 for super admin on tenant scoped, got %d", rec.Code)
		}
	})

	// 12. me_allowed_routes_match_permissions
	t.Run("me_allowed_routes_match_permissions", func(t *testing.T) {
		token := issueTestToken(t, store, key, "alice@acme.example")
		req := httptest.NewRequest(http.MethodGet, "/me", nil)
		req.Header.Set("Authorization", "Bearer "+token)
		rec := httptest.NewRecorder()
		e.ServeHTTP(rec, req)

		if rec.Code != http.StatusOK {
			t.Fatalf("expected 200 for /me, got %d", rec.Code)
		}
		var resp map[string]interface{}
		json.Unmarshal(rec.Body.Bytes(), &resp)
		allowedRoutes, ok := resp["allowed_routes"].([]interface{})
		if !ok || len(allowedRoutes) == 0 {
			t.Error("expected allowed_routes to be populated")
		}
		hasUsersRoute := false
		for _, r := range allowedRoutes {
			route := r.(map[string]interface{})
			if route["path"] == "/users" {
				hasUsersRoute = true
			}
		}
		if !hasUsersRoute {
			t.Error("expected allowed_routes to contain /users")
		}
	})
}
