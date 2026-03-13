package main

import (
	"net/http"

	"github.com/labstack/echo/v4"
)

func main() {
	app := echo.New()

	app.GET("/healthz", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]string{
			"status":  "ok",
			"service": "go-echo-example",
		})
	})

	app.GET("/reports/summary", func(c echo.Context) error {
		tenantID := c.QueryParam("tenant_id")
		if tenantID == "" {
			tenantID = "acme"
		}
		return c.JSON(http.StatusOK, []map[string]interface{}{
			{
				"report_id":    "daily-signups",
				"tenant_id":    tenantID,
				"total_events": 42,
			},
		})
	})

	app.Logger.Fatal(app.Start(":8080"))
}
