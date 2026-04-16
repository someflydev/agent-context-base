//go:build smoke

package smoke

import (
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/handlers"

	"github.com/labstack/echo/v4"
)

func setupServer(t *testing.T) *echo.Echo {
	store, err := data.ReadFixtures(data.GetFixturePath())
	if err != nil {
		t.Fatalf("failed to load fixtures: %v", err)
	}

	e := echo.New()
	e.Use(func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			c.Set("store", store)
			return next(c)
		}
	})

	e.GET("/health", handlers.HealthHandler)
	e.GET("/", handlers.OverviewPageHandler)
	e.GET("/trends", handlers.TrendsPageHandler)
	e.GET("/services", handlers.ServicesPageHandler)
	e.GET("/distributions", handlers.DistributionsPageHandler)
	e.GET("/heatmap", handlers.HeatmapPageHandler)
	e.GET("/funnel", handlers.FunnelPageHandler)
	e.GET("/incidents", handlers.IncidentsPageHandler)
	e.GET("/fragments/chart", handlers.ChartFragmentHandler)
	e.GET("/fragments/summary", handlers.SummaryFragmentHandler)
	e.GET("/fragments/details", handlers.DetailsFragmentHandler)

	return e
}

func TestSmokeRoutes(t *testing.T) {
	e := setupServer(t)
	ts := httptest.NewServer(e)
	defer ts.Close()

	paths := []string{
		"/", "/trends", "/services", "/distributions", "/heatmap", "/funnel", "/incidents",
		"/health",
		"/fragments/chart?view=trends",
		"/fragments/summary?view=trends",
		"/fragments/details?view=services&service=billing-api",
		"/trends?environment=production",
	}

	for _, p := range paths {
		res, err := http.Get(ts.URL + p)
		if err != nil {
			t.Fatalf("failed to get %s: %v", p, err)
		}
		if res.StatusCode != 200 {
			t.Errorf("expected 200 for %s, got %d", p, res.StatusCode)
		}
		body, _ := io.ReadAll(res.Body)
		res.Body.Close()
		if len(body) == 0 {
			t.Errorf("expected non-empty body for %s", p)
		}

		if p == "/health" {
			var m map[string]string
			if err := json.Unmarshal(body, &m); err != nil || m["status"] != "ok" {
				t.Errorf("expected {\"status\": \"ok\"} for /health")
			}
		}

		if p == "/fragments/chart?view=trends" {
			if !strings.Contains(strings.ToLower(string(body)), "plotly") {
				t.Errorf("expected plotly in chart fragment")
			}
		}
	}
}
