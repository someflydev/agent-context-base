package routes

import (
	"net/http"

	"canonical-auth/internal/auth"
	"canonical-auth/internal/domain"

	"github.com/labstack/echo/v4"
)

type UsersRoutes struct {
	Store *domain.InMemoryStore
}

func (r *UsersRoutes) List(c echo.Context) error {
	authCtx, ok := c.Get("auth").(*auth.AuthContext)
	if !ok {
		return echo.NewHTTPError(http.StatusInternalServerError, "missing auth context")
	}
	if authCtx.TenantID == nil {
		return echo.NewHTTPError(http.StatusForbidden, "tenant scoped route")
	}

	var tenantUsers []domain.User
	for _, u := range r.Store.Users {
		if r.Store.VerifyMembership(u.ID, *authCtx.TenantID) {
			tenantUsers = append(tenantUsers, u)
		}
	}

	if tenantUsers == nil {
		tenantUsers = []domain.User{}
	}

	return c.JSON(http.StatusOK, tenantUsers)
}

func (r *UsersRoutes) Invite(c echo.Context) error {
	authCtx, ok := c.Get("auth").(*auth.AuthContext)
	if !ok || authCtx.TenantID == nil {
		return echo.NewHTTPError(http.StatusForbidden, "tenant scoped route")
	}

	return c.JSON(http.StatusCreated, map[string]string{"message": "User invited"})
}

func (r *UsersRoutes) Get(c echo.Context) error {
	authCtx, ok := c.Get("auth").(*auth.AuthContext)
	if !ok || authCtx.TenantID == nil {
		return echo.NewHTTPError(http.StatusForbidden, "tenant scoped route")
	}

	id := c.Param("id")
	user, found := r.Store.GetUserByID(id)
	if !found {
		return echo.NewHTTPError(http.StatusNotFound, "user not found")
	}

	if !r.Store.VerifyMembership(user.ID, *authCtx.TenantID) {
		return echo.NewHTTPError(http.StatusForbidden, "cross tenant access denied")
	}

	return c.JSON(http.StatusOK, user)
}

func (r *UsersRoutes) Update(c echo.Context) error {
	authCtx, ok := c.Get("auth").(*auth.AuthContext)
	if !ok || authCtx.TenantID == nil {
		return echo.NewHTTPError(http.StatusForbidden, "tenant scoped route")
	}

	id := c.Param("id")
	user, found := r.Store.GetUserByID(id)
	if !found {
		return echo.NewHTTPError(http.StatusNotFound, "user not found")
	}

	if !r.Store.VerifyMembership(user.ID, *authCtx.TenantID) {
		return echo.NewHTTPError(http.StatusForbidden, "cross tenant access denied")
	}

	return c.JSON(http.StatusOK, map[string]string{"message": "User updated"})
}
