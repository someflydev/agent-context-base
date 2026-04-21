package tests

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"canonical-auth/internal/registry"
)

func TestMeHandler_CorrectFields(t *testing.T) {
	e, store, key := setupTestApp(t)
	token := issueTestToken(t, store, key, "alice@acme.example")

	req := httptest.NewRequest(http.MethodGet, "/me", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	rec := httptest.NewRecorder()
	e.ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", rec.Code)
	}

	var resp map[string]interface{}
	if err := json.Unmarshal(rec.Body.Bytes(), &resp); err != nil {
		t.Fatalf("failed to parse /me response: %v", err)
	}

	expectedFields := []string{
		"sub", "email", "display_name", "tenant_id", "tenant_name", "tenant_role",
		"groups", "permissions", "acl_ver", "allowed_routes", "guide_sections",
		"issued_at", "expires_at",
	}

	for _, f := range expectedFields {
		if _, ok := resp[f]; !ok {
			t.Errorf("missing field in /me response: %s", f)
		}
	}

	if resp["tenant_role"] != "tenant_member" {
		t.Errorf("expected tenant_role tenant_member, got %v", resp["tenant_role"])
	}
}

func TestMeHandler_AllowedRoutesFiltered(t *testing.T) {
	e, store, key := setupTestApp(t)
	token := issueTestToken(t, store, key, "bob@acme.example") // bob has billing but not iam:user:invite

	req := httptest.NewRequest(http.MethodGet, "/me", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	rec := httptest.NewRecorder()
	e.ServeHTTP(rec, req)

	var resp map[string]interface{}
	json.Unmarshal(rec.Body.Bytes(), &resp)

	allowedRoutes := resp["allowed_routes"].([]interface{})
	
	hasUserRead := false
	hasUserInvite := false
	for _, r := range allowedRoutes {
		route := r.(map[string]interface{})
		if route["permission"] == "iam:user:read" {
			hasUserRead = true
		}
		if route["permission"] == "iam:user:invite" {
			hasUserInvite = true
		}
	}

	if !hasUserRead {
		t.Error("expected bob to have iam:user:read route")
	}
	if hasUserInvite {
		t.Error("expected bob to NOT have iam:user:invite route")
	}
}

func TestMeHandler_SuperAdminShape(t *testing.T) {
	e, store, key := setupTestApp(t)
	token := issueTestToken(t, store, key, "superadmin@tenantcore.dev")

	req := httptest.NewRequest(http.MethodGet, "/me", nil)
	req.Header.Set("Authorization", "Bearer "+token)
	rec := httptest.NewRecorder()
	e.ServeHTTP(rec, req)

	var resp struct {
		TenantID      *string                  `json:"tenant_id"`
		TenantRole    string                   `json:"tenant_role"`
		Groups        []string                 `json:"groups"`
		AllowedRoutes []registry.RouteMetadata `json:"allowed_routes"`
	}
	json.Unmarshal(rec.Body.Bytes(), &resp)

	if resp.TenantID != nil {
		t.Error("expected super admin tenant_id to be nil")
	}
	if resp.TenantRole != "super_admin" {
		t.Errorf("expected tenant_role super_admin, got %s", resp.TenantRole)
	}
	if len(resp.Groups) != 0 {
		t.Error("expected super admin groups to be empty")
	}

	hasAdminRoute := false
	hasTenantScopedRoute := false
	for _, r := range resp.AllowedRoutes {
		if r.SuperAdminOnly {
			hasAdminRoute = true
		}
		if r.TenantScoped {
			hasTenantScopedRoute = true
		}
	}

	if !hasAdminRoute {
		t.Error("expected super admin to have admin routes")
	}
	if hasTenantScopedRoute {
		t.Error("expected super admin allowed_routes to not include tenant scoped routes")
	}
}
