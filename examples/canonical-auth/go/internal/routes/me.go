package routes

import (
	"net/http"
	"time"

	"canonical-auth/internal/auth"
	"canonical-auth/internal/domain"
	"canonical-auth/internal/registry"

	"github.com/labstack/echo/v4"
)

type MeRoutes struct {
	Store *domain.InMemoryStore
}

type MeResponse struct {
	Sub           string                   `json:"sub"`
	Email         string                   `json:"email"`
	DisplayName   string                   `json:"display_name"`
	TenantID      *string                  `json:"tenant_id"`
	TenantName    string                   `json:"tenant_name,omitempty"`
	TenantRole    string                   `json:"tenant_role"`
	Groups        []string                 `json:"groups"`
	Permissions   []string                 `json:"permissions"`
	ACLVer        int                      `json:"acl_ver"`
	AllowedRoutes []registry.RouteMetadata `json:"allowed_routes"`
	GuideSections []string                 `json:"guide_sections"`
	IssuedAt      time.Time                `json:"issued_at"`
	ExpiresAt     time.Time                `json:"expires_at"`
}

func (r *MeRoutes) Me(c echo.Context) error {
	authCtx, ok := c.Get("auth").(*auth.AuthContext)
	if !ok {
		return echo.NewHTTPError(http.StatusInternalServerError, "missing auth context")
	}

	user, ok := r.Store.GetUserByID(authCtx.Sub)
	if !ok {
		return echo.NewHTTPError(http.StatusUnauthorized, "user not found")
	}

	var tenantName string
	if authCtx.TenantID != nil {
		tenantName = r.Store.GetTenantName(*authCtx.TenantID)
	}

	isSuperAdmin := authCtx.TenantRole == "super_admin"
	allowedRoutes := registry.GetAllowedRoutes(authCtx.Permissions, isSuperAdmin)

	var guideSections []string
	if !isSuperAdmin {
		guideSections = []string{"User Management", "Billing"}
	} else {
		guideSections = []string{}
	}

	groups := authCtx.Groups
	if groups == nil {
		groups = []string{}
	}
	permissions := authCtx.Permissions
	if permissions == nil {
		permissions = []string{}
	}

	resp := MeResponse{
		Sub:           authCtx.Sub,
		Email:         authCtx.Email,
		DisplayName:   user.DisplayName,
		TenantID:      authCtx.TenantID,
		TenantName:    tenantName,
		TenantRole:    authCtx.TenantRole,
		Groups:        groups,
		Permissions:   permissions,
		ACLVer:        authCtx.ACLVer,
		AllowedRoutes: allowedRoutes,
		GuideSections: guideSections,
		IssuedAt:      authCtx.IssuedAt,
		ExpiresAt:     authCtx.ExpiresAt,
	}

	return c.JSON(http.StatusOK, resp)
}
