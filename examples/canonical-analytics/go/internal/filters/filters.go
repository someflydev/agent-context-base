package filters

import (
	"time"

	"github.com/labstack/echo/v4"
)

type FilterState struct {
	DateFrom    *time.Time
	DateTo      *time.Time
	Services    []string
	Severity    []string
	Environment []string
}

func ParseFilterState(c echo.Context) FilterState {
	state := FilterState{}

	// QueryParams returns map[string][]string
	if services, ok := c.QueryParams()["services"]; ok {
		state.Services = filterEmpty(services)
	}
	if severity, ok := c.QueryParams()["severity"]; ok {
		state.Severity = filterEmpty(severity)
	}
	if environment, ok := c.QueryParams()["environment"]; ok {
		state.Environment = filterEmpty(environment)
	}

	dateFromStr := c.QueryParam("date_from")
	if dateFromStr != "" {
		if t, err := time.Parse("2006-01-02", dateFromStr); err == nil {
			state.DateFrom = &t
		}
	}

	dateToStr := c.QueryParam("date_to")
	if dateToStr != "" {
		if t, err := time.Parse("2006-01-02", dateToStr); err == nil {
			state.DateTo = &t
		}
	}

	return state
}

func filterEmpty(items []string) []string {
	var result []string
	for _, item := range items {
		if item != "" {
			result = append(result, item)
		}
	}
	return result
}

func (f FilterState) ContainsService(s string) bool {
	if len(f.Services) == 0 {
		return true
	}
	for _, v := range f.Services {
		if v == s {
			return true
		}
	}
	return false
}

func (f FilterState) ContainsEnvironment(e string) bool {
	if len(f.Environment) == 0 {
		return true
	}
	for _, v := range f.Environment {
		if v == e {
			return true
		}
	}
	return false
}

func (f FilterState) ContainsSeverity(s string) bool {
	if len(f.Severity) == 0 {
		return true
	}
	for _, v := range f.Severity {
		if v == s {
			return true
		}
	}
	return false
}

func (f FilterState) InDateRange(t time.Time) bool {
	if f.DateFrom != nil && t.Before(*f.DateFrom) {
		return false
	}
	if f.DateTo != nil {
		// Include the end date fully (e.g. up to 23:59:59)
		endOfDay := f.DateTo.Add(24*time.Hour - time.Nanosecond)
		if t.After(endOfDay) {
			return false
		}
	}
	return true
}
