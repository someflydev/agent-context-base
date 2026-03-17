// playwright-go-htmx-example_test.go
//
// Canonical example: Playwright e2e test for a Go/Echo/templ HTMX backend.
//
// Setup (run once after cloning):
//
//	go get github.com/playwright-community/playwright-go
//	go run github.com/playwright-community/playwright-go/cmd/playwright install --with-deps chromium
//
// Run:
//
//	go test ./tests/e2e/...
//
// The backend must be running before the test suite executes. Start it with:
//
//	go run ./cmd/server
//
// Requires Go 1.24+ for the -tool approach used with templ.

package e2e

import (
	"fmt"
	"os"
	"testing"

	playwright "github.com/playwright-community/playwright-go"
)

var (
	pw      *playwright.Playwright
	browser playwright.Browser
)

// TestMain starts and stops the Playwright browser process for the whole suite.
// Individual tests create and close their own pages.
func TestMain(m *testing.M) {
	var err error

	pw, err = playwright.Run()
	if err != nil {
		fmt.Fprintf(os.Stderr, "could not start Playwright: %v\n", err)
		os.Exit(1)
	}

	browser, err = pw.Chromium.Launch()
	if err != nil {
		fmt.Fprintf(os.Stderr, "could not launch Chromium: %v\n", err)
		os.Exit(1)
	}

	code := m.Run()

	if err = browser.Close(); err != nil {
		fmt.Fprintf(os.Stderr, "could not close browser: %v\n", err)
	}
	if err = pw.Stop(); err != nil {
		fmt.Fprintf(os.Stderr, "could not stop Playwright: %v\n", err)
	}

	os.Exit(code)
}

// TestHTMXFilterFragment verifies that clicking a filter triggers an HTMX swap
// and that the resulting fragment reflects the correct backend query result.
//
// Arrange → Act → Assert pattern. Assertions are semantic (count, label text),
// not visual. This mirrors the TypeScript canonical examples in this directory.
func TestHTMXFilterFragment(t *testing.T) {
	page, err := browser.NewPage()
	if err != nil {
		t.Fatalf("could not create page: %v", err)
	}
	defer page.Close()

	// Arrange: navigate to the main listing page
	if _, err = page.Goto("http://localhost:8080/"); err != nil {
		t.Fatalf("could not navigate to app: %v", err)
	}

	// Act: activate a category filter
	if err = page.Locator("[data-filter='category'][data-value='electronics']").Click(); err != nil {
		t.Fatalf("could not click category filter: %v", err)
	}

	// Wait for the HTMX fragment swap to complete
	if err = page.Locator("#results-list").WaitFor(); err != nil {
		t.Fatalf("results list did not appear after filter click: %v", err)
	}

	// Assert: result items in the swapped fragment match the filter predicate
	count, err := page.Locator("#results-list [data-item]").Count()
	if err != nil {
		t.Fatalf("could not count result items: %v", err)
	}
	if count != 12 {
		t.Errorf("expected 12 filtered results, got %d", count)
	}

	// Assert: the result count label exposed by the backend matches the item count
	countText, err := page.Locator("[data-result-count]").TextContent()
	if err != nil {
		t.Fatalf("could not read result count label: %v", err)
	}
	if countText != "12" {
		t.Errorf("expected result count label '12', got %q", countText)
	}
}

// TestHTMXFilterClear verifies that clearing an active filter restores the
// full result set and updates the count label to match.
func TestHTMXFilterClear(t *testing.T) {
	page, err := browser.NewPage()
	if err != nil {
		t.Fatalf("could not create page: %v", err)
	}
	defer page.Close()

	// Arrange: navigate and apply a filter first
	if _, err = page.Goto("http://localhost:8080/"); err != nil {
		t.Fatalf("could not navigate to app: %v", err)
	}
	if err = page.Locator("[data-filter='category'][data-value='electronics']").Click(); err != nil {
		t.Fatalf("could not apply filter: %v", err)
	}
	if err = page.Locator("#results-list").WaitFor(); err != nil {
		t.Fatalf("results list did not appear: %v", err)
	}

	// Act: clear the filter
	if err = page.Locator("[data-clear-filters]").Click(); err != nil {
		t.Fatalf("could not click clear filters: %v", err)
	}
	if err = page.Locator("#results-list").WaitFor(); err != nil {
		t.Fatalf("results list did not reappear after clear: %v", err)
	}

	// Assert: full result set is restored
	count, err := page.Locator("#results-list [data-item]").Count()
	if err != nil {
		t.Fatalf("could not count result items: %v", err)
	}
	if count != 100 {
		t.Errorf("expected 100 results after clearing filter, got %d", count)
	}
}
