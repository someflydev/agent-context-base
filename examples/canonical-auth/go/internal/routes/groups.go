package routes

import (
	"net/http"

	"canonical-auth/internal/auth"
	"canonical-auth/internal/domain"

	"github.com/labstack/echo/v4"
)

type GroupsRoutes struct {
	Store *domain.InMemoryStore
}

func (r *GroupsRoutes) List(c echo.Context) error {
	authCtx, ok := c.Get("auth").(*auth.AuthContext)
	if !ok || authCtx.TenantID == nil {
		return echo.NewHTTPError(http.StatusForbidden, "tenant scoped route")
	}

	var tenantGroups []domain.Group
	for _, g := range r.Store.Groups {
		if g.TenantID == *authCtx.TenantID {
			tenantGroups = append(tenantGroups, g)
		}
	}

	if tenantGroups == nil {
		tenantGroups = []domain.Group{}
	}

	return c.JSON(http.StatusOK, tenantGroups)
}

func (r *GroupsRoutes) Create(c echo.Context) error {
	authCtx, ok := c.Get("auth").(*auth.AuthContext)
	if !ok || authCtx.TenantID == nil {
		return echo.NewHTTPError(http.StatusForbidden, "tenant scoped route")
	}

	return c.JSON(http.StatusCreated, map[string]string{"message": "Group created"})
}

func (r *GroupsRoutes) AssignPermission(c echo.Context) error {
	authCtx, ok := c.Get("auth").(*auth.AuthContext)
	if !ok || authCtx.TenantID == nil {
		return echo.NewHTTPError(http.StatusForbidden, "tenant scoped route")
	}

	groupID := c.Param("id")

	var group *domain.Group
	for _, g := range r.Store.Groups {
		if g.ID == groupID && g.TenantID == *authCtx.TenantID {
			group = &g
			break
		}
	}

	if group == nil {
		return echo.NewHTTPError(http.StatusNotFound, "group not found in tenant")
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "Permission assigned"})
}

func (r *GroupsRoutes) AssignUser(c echo.Context) error {
	authCtx, ok := c.Get("auth").(*auth.AuthContext)
	if !ok || authCtx.TenantID == nil {
		return echo.NewHTTPError(http.StatusForbidden, "tenant scoped route")
	}

	groupID := c.Param("id")

	var group *domain.Group
	for _, g := range r.Store.Groups {
		if g.ID == groupID && g.TenantID == *authCtx.TenantID {
			group = &g
			break
		}
	}

	if group == nil {
		return echo.NewHTTPError(http.StatusNotFound, "group not found in tenant")
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "User assigned"})
}
