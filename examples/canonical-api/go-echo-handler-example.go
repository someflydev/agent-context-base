package http

import (
	"net/http"
	"strconv"

	"github.com/labstack/echo/v4"

	"example/internal/services"
	"example/internal/views"
)

type ReportHandler struct {
	Reports *services.ReportService
}

func (handler ReportHandler) Register(group *echo.Group) {
	group.GET("/tenants/:tenantID/reports", handler.ListRecent)
}

func (handler ReportHandler) ListRecent(c echo.Context) error {
	tenantID := c.Param("tenantID")
	limit, err := strconv.Atoi(c.QueryParam("limit"))
	if err != nil || limit <= 0 {
		limit = 10
	}

	summaries, err := handler.Reports.ListRecent(c.Request().Context(), tenantID, limit)
	if err != nil {
		return echo.NewHTTPError(http.StatusBadGateway, "could not load report summaries")
	}

	c.Response().Header().Set(echo.HeaderContentType, echo.MIMETextHTMLCharsetUTF8)
	return views.ReportSummaryList(summaries).Render(c.Request().Context(), c.Response())
}

