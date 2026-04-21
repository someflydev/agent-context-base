package routes

import (
	"net/http"

	"canonical-auth/internal/domain"

	"github.com/labstack/echo/v4"
)

type AdminRoutes struct {
	Store *domain.InMemoryStore
}

func (r *AdminRoutes) ListTenants(c echo.Context) error {
	return c.JSON(http.StatusOK, r.Store.Tenants)
}

func (r *AdminRoutes) CreateTenant(c echo.Context) error {
	return c.JSON(http.StatusCreated, map[string]string{"message": "Tenant created"})
}
