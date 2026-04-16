//go:build unit

package unit

import (
	"net/http"
	"net/url"
	"testing"

	"analytics-workbench-go/internal/filters"
	"github.com/labstack/echo/v4"
)

func TestParseEmptyQuery(t *testing.T) {
	e := echo.New()
	req, _ := http.NewRequest(http.MethodGet, "/", nil)
	c := e.NewContext(req, nil)
	f := filters.ParseFilterState(c)
	if len(f.Services) != 0 || len(f.Environment) != 0 {
		t.Errorf("expected empty slices")
	}
}

func TestParseMultiService(t *testing.T) {
	e := echo.New()
	q := make(url.Values)
	q.Add("services", "api")
	q.Add("services", "web")
	req, _ := http.NewRequest(http.MethodGet, "/?"+q.Encode(), nil)
	c := e.NewContext(req, nil)
	f := filters.ParseFilterState(c)
	if len(f.Services) != 2 {
		t.Errorf("expected 2 services")
	}
}

func TestParseDateRange(t *testing.T) {
	e := echo.New()
	q := make(url.Values)
	q.Add("date_from", "2025-01-01")
	q.Add("date_to", "2025-01-31")
	req, _ := http.NewRequest(http.MethodGet, "/?"+q.Encode(), nil)
	c := e.NewContext(req, nil)
	f := filters.ParseFilterState(c)
	if f.DateFrom == nil || f.DateTo == nil {
		t.Errorf("expected dates to be parsed")
	}
}
