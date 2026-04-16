package main

import (
	"log"

	"analytics-workbench-go/internal/config"
	"analytics-workbench-go/internal/data"
	"analytics-workbench-go/internal/handlers"

	"github.com/labstack/echo/v4"
)

func main() {
	cfg := config.Load()

	store, err := data.ReadFixtures(cfg.FixturePath)
	if err != nil {
		log.Fatalf("Failed to load fixtures: %v", err)
	}

	e := echo.New()
	
	// Inject store
	e.Use(func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			c.Set("store", store)
			return next(c)
		}
	})

	// Health
	e.GET("/health", handlers.HealthHandler)

	// Pages
	e.GET("/", handlers.OverviewPageHandler)
	e.GET("/trends", handlers.TrendsPageHandler)
	e.GET("/services", handlers.ServicesPageHandler)
	e.GET("/distributions", handlers.DistributionsPageHandler)
	e.GET("/heatmap", handlers.HeatmapPageHandler)
	e.GET("/funnel", handlers.FunnelPageHandler)
	e.GET("/incidents", handlers.IncidentsPageHandler)

	// Fragments
	e.GET("/fragments/chart", handlers.ChartFragmentHandler)
	e.GET("/fragments/summary", handlers.SummaryFragmentHandler)
	e.GET("/fragments/details", handlers.DetailsFragmentHandler)

	if err := e.Start(":" + cfg.Port); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
