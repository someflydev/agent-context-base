package routes

import (
	"net/http"

	"github.com/labstack/echo/v4"
)

type HealthRoutes struct{}

func (r *HealthRoutes) Health(c echo.Context) error {
	return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
}
