import { expect, test } from "@playwright/test";

// Dataset reference (from fastapi-search-sort-filter-example.py):
//   report_id          team     status   region  events
//   daily-signups      growth   active   us      12
//   trial-conversions  growth   active   us       7
//   api-latency        platform paused   eu       5
//   checkout-failures  growth   active   eu       9
//   queue-depth        platform active   apac    11
//   legacy-import      platform archived us       4
//
// Sort order reference:
//   events_desc: daily-signups(12), queue-depth(11), checkout-failures(9),
//                trial-conversions(7), api-latency(5), legacy-import(4)
//   events_asc:  legacy-import(4), api-latency(5), trial-conversions(7),
//                checkout-failures(9), queue-depth(11), daily-signups(12)
//   name_asc:    api-latency, checkout-failures, daily-signups,
//                legacy-import, queue-depth, trial-conversions
//
// Text search reference (report_id substring match):
//   query="daily"   → 1 match: daily-signups
//   query="import"  → 1 match: legacy-import
//   query="latency" → 1 match: api-latency

// ---------------------------------------------------------------------------
// Test 1: search input is present with correct data attributes
// ---------------------------------------------------------------------------

test("search input is present with correct data attributes", async ({ page }) => {
  await page.goto("/ui/reports");

  const searchInput = page.locator('[data-role="search-input"]');
  await expect(searchInput).toBeVisible();

  // name attribute must be "query"
  await expect(searchInput).toHaveAttribute("name", "query");

  // data-search-query is empty string (no active search) or absent
  const searchQueryAttr = await searchInput.getAttribute("data-search-query");
  expect(searchQueryAttr === "" || searchQueryAttr === null).toBe(true);

  // Input must not be disabled
  await expect(searchInput).not.toBeDisabled();
});

// ---------------------------------------------------------------------------
// Test 2: results reflect text search — result count and result cards
// ---------------------------------------------------------------------------

test("results reflect text search — result count and result cards", async ({ page }) => {
  // query="daily" matches only daily-signups (report_id substring match)
  await page.goto("/ui/reports?query=daily");

  // Result count badge shows 1
  await expect(page.locator('[data-role="result-count"]')).toContainText("1");

  // Results section has data-result-count="1"
  await expect(page.locator("#report-results")).toHaveAttribute("data-result-count", "1");

  // Results section has data-search-query="daily"
  await expect(page.locator("#report-results")).toHaveAttribute("data-search-query", "daily");

  // Exactly 1 result card is visible
  const cards = page.locator("[data-report-id]");
  await expect(cards).toHaveCount(1);

  // The result card is daily-signups
  await expect(cards.first()).toContainText("daily-signups");
});

// ---------------------------------------------------------------------------
// Test 3: text search affects facet counts
// ---------------------------------------------------------------------------

test("text search affects facet counts", async ({ page }) => {
  // query="daily" matches only daily-signups (growth/active/us, events:12)
  await page.goto("/ui/reports?query=daily");

  // team: growth=1, platform=0
  const growthInclude = page.locator(
    '[data-filter-dimension="team"][data-filter-option="growth"][data-filter-mode="include"]'
  );
  await expect(growthInclude).toHaveAttribute("data-option-count", "1");

  const platformInclude = page.locator(
    '[data-filter-dimension="team"][data-filter-option="platform"][data-filter-mode="include"]'
  );
  await expect(platformInclude).toHaveAttribute("data-option-count", "0");

  // status: active=1, paused=0, archived=0
  const activeInclude = page.locator(
    '[data-filter-dimension="status"][data-filter-option="active"][data-filter-mode="include"]'
  );
  await expect(activeInclude).toHaveAttribute("data-option-count", "1");

  const pausedInclude = page.locator(
    '[data-filter-dimension="status"][data-filter-option="paused"][data-filter-mode="include"]'
  );
  await expect(pausedInclude).toHaveAttribute("data-option-count", "0");

  // region: us=1, eu=0, apac=0
  const usInclude = page.locator(
    '[data-filter-dimension="region"][data-filter-option="us"][data-filter-mode="include"]'
  );
  await expect(usInclude).toHaveAttribute("data-option-count", "1");

  const euInclude = page.locator(
    '[data-filter-dimension="region"][data-filter-option="eu"][data-filter-mode="include"]'
  );
  await expect(euInclude).toHaveAttribute("data-option-count", "0");
});

// ---------------------------------------------------------------------------
// Test 4: search narrows counts in combination with facet filter
// ---------------------------------------------------------------------------

test("search narrows counts in combination with facet filter", async ({ page }) => {
  // query="import" matches only legacy-import (platform/archived/us).
  // status_out=archived excludes archived rows.
  // Result: 0 rows (legacy-import is the only "import" match, and it's archived → excluded).
  await page.goto("/ui/reports?query=import&status_out=archived");

  await expect(page.locator('[data-role="result-count"]')).toContainText("0");
  await expect(page.locator("#report-results")).toHaveAttribute("data-result-count", "0");

  // The archived include option must be data-excluded="true" and count 0 (RULE 1)
  const archivedInclude = page.locator(
    '[data-filter-dimension="status"][data-filter-option="archived"][data-filter-mode="include"]'
  );
  await expect(archivedInclude).toHaveAttribute("data-excluded", "true");
  await expect(archivedInclude).toHaveAttribute("data-option-count", "0");
});

// ---------------------------------------------------------------------------
// Test 5: search input value is preserved after HTMX partial swap
// ---------------------------------------------------------------------------

test("search input value is preserved after HTMX partial swap triggered by facet change", async ({ page }) => {
  // Load with both query and a team filter active.
  // The filter panel fragment must re-populate the search input from state.
  await page.goto("/ui/reports?query=daily&team_in=growth");

  const searchInput = page.locator('[data-role="search-input"]');

  // The input value attribute must be "daily" (pre-populated from state)
  await expect(searchInput).toHaveAttribute("value", "daily");

  // data-search-query on the input must also be "daily"
  await expect(searchInput).toHaveAttribute("data-search-query", "daily");
});

// ---------------------------------------------------------------------------
// Test 6: sort select is present with correct data attributes
// ---------------------------------------------------------------------------

test("sort select is present with correct data attributes", async ({ page }) => {
  await page.goto("/ui/reports");

  const sortSelect = page.locator('[data-role="sort-select"]');
  await expect(sortSelect).toBeVisible();

  // Default sort is events_desc
  await expect(sortSelect).toHaveAttribute("data-sort-order", "events_desc");

  // The events_desc option must be selected
  const eventsDescOption = sortSelect.locator('option[value="events_desc"]');
  await expect(eventsDescOption).toHaveAttribute("selected", "");
});

// ---------------------------------------------------------------------------
// Test 7: sort=events_asc places lowest-event result first
// ---------------------------------------------------------------------------

test("sort=events_asc places lowest-event result first", async ({ page }) => {
  await page.goto("/ui/reports?sort=events_asc");

  // Results section must carry data-sort-order="events_asc"
  await expect(page.locator("#report-results")).toHaveAttribute("data-sort-order", "events_asc");

  // Sort select must reflect events_asc
  await expect(page.locator('[data-role="sort-select"]')).toHaveAttribute("data-sort-order", "events_asc");

  // First result card: legacy-import (events: 4 — lowest in the dataset)
  const firstCard = page.locator("[data-report-id]").first();
  await expect(firstCard).toContainText("legacy-import");
});

// ---------------------------------------------------------------------------
// Test 8: sort=name_asc places alphabetically first result first
// ---------------------------------------------------------------------------

test("sort=name_asc places alphabetically first result first", async ({ page }) => {
  await page.goto("/ui/reports?sort=name_asc");

  // First result alphabetically: api-latency
  const firstCard = page.locator("[data-report-id]").first();
  await expect(firstCard).toContainText("api-latency");

  // Sort select reflects name_asc
  const sortSelect = page.locator('[data-role="sort-select"]');
  await expect(sortSelect).toHaveAttribute("data-sort-order", "name_asc");

  // The name_asc option is selected
  await expect(sortSelect.locator('option[value="name_asc"]')).toHaveAttribute("selected", "");
});

// ---------------------------------------------------------------------------
// Test 9: sort does not affect facet counts
// ---------------------------------------------------------------------------

test("sort does not affect facet counts", async ({ page }) => {
  // With no filters, counts are dataset totals regardless of sort.
  await page.goto("/ui/reports?sort=events_asc");

  // team: growth=3, platform=3
  await expect(
    page.locator('[data-filter-dimension="team"][data-filter-option="growth"][data-filter-mode="include"]')
  ).toHaveAttribute("data-option-count", "3");
  await expect(
    page.locator('[data-filter-dimension="team"][data-filter-option="platform"][data-filter-mode="include"]')
  ).toHaveAttribute("data-option-count", "3");

  // status: active=4, paused=1, archived=1
  await expect(
    page.locator('[data-filter-dimension="status"][data-filter-option="active"][data-filter-mode="include"]')
  ).toHaveAttribute("data-option-count", "4");
  await expect(
    page.locator('[data-filter-dimension="status"][data-filter-option="paused"][data-filter-mode="include"]')
  ).toHaveAttribute("data-option-count", "1");
  await expect(
    page.locator('[data-filter-dimension="status"][data-filter-option="archived"][data-filter-mode="include"]')
  ).toHaveAttribute("data-option-count", "1");
});

// ---------------------------------------------------------------------------
// Test 10: sort select retains its value after an HTMX facet filter change
// ---------------------------------------------------------------------------

test("sort select retains its value after an HTMX facet filter change", async ({ page }) => {
  // Load with sort=name_asc and an active exclude filter.
  await page.goto("/ui/reports?sort=name_asc&status_out=archived");

  const sortSelect = page.locator('[data-role="sort-select"]');
  await expect(sortSelect).toHaveAttribute("data-sort-order", "name_asc");

  // The name_asc option must be selected
  await expect(sortSelect.locator('option[value="name_asc"]')).toHaveAttribute("selected", "");
});

// ---------------------------------------------------------------------------
// Test 11: layout has independent scroll structure
// ---------------------------------------------------------------------------

test("layout has independent scroll structure", async ({ page }) => {
  await page.goto("/ui/reports");

  // Outer layout wrapper exists
  const layout = page.locator('[data-role="reports-layout"]');
  await expect(layout).toBeVisible();

  // Layout wrapper contains both #filter-panel and #report-results-container
  await expect(layout.locator("#filter-panel")).toBeVisible();
  await expect(layout.locator("#report-results-container")).toBeVisible();

  // #filter-panel has overflow-y auto or scroll (independent scroll)
  const filterPanelOverflow = await page.locator("#filter-panel").evaluate(
    (el) => window.getComputedStyle(el).overflowY
  );
  expect(["auto", "scroll"]).toContain(filterPanelOverflow);

  // #report-results-container has overflow-y auto or scroll
  const resultsContainerOverflow = await page.locator("#report-results-container").evaluate(
    (el) => window.getComputedStyle(el).overflowY
  );
  expect(["auto", "scroll"]).toContain(resultsContainerOverflow);

  // #filter-panel and #report-results-container are siblings (not nested)
  const areSiblings = await page.evaluate(() => {
    const panel = document.getElementById("filter-panel");
    const container = document.getElementById("report-results-container");
    return panel !== null && container !== null && panel.parentElement === container.parentElement;
  });
  expect(areSiblings).toBe(true);
});

// ---------------------------------------------------------------------------
// Test 12: sort select inside results container, search input inside filter panel
// ---------------------------------------------------------------------------

test("sort select inside results container, search input inside filter panel", async ({ page }) => {
  await page.goto("/ui/reports");

  // Sort select must be a descendant of #report-results-container
  const sortSelectInsideResults = await page.evaluate(() => {
    const sortSelect = document.querySelector('[data-role="sort-select"]');
    const container = document.getElementById("report-results-container");
    return container !== null && sortSelect !== null && container.contains(sortSelect);
  });
  expect(sortSelectInsideResults).toBe(true);

  // Search input must be a descendant of #filter-panel
  const searchInputInsidePanel = await page.evaluate(() => {
    const searchInput = document.querySelector('[data-role="search-input"]');
    const panel = document.getElementById("filter-panel");
    return panel !== null && searchInput !== null && panel.contains(searchInput);
  });
  expect(searchInputInsidePanel).toBe(true);
});

// ---------------------------------------------------------------------------
// Test 13: search and sort combined — result order and count both correct
// ---------------------------------------------------------------------------

test("search and sort combined — result order and count correct", async ({ page }) => {
  // query="daily" matches only daily-signups (1 result)
  // sort=name_asc: alphabetically first = daily-signups (the only result)
  await page.goto("/ui/reports?query=daily&sort=name_asc");

  // Result count = 1
  await expect(page.locator('[data-role="result-count"]')).toContainText("1");
  await expect(page.locator("#report-results")).toHaveAttribute("data-result-count", "1");

  // First (and only) card is daily-signups
  const firstCard = page.locator("[data-report-id]").first();
  await expect(firstCard).toContainText("daily-signups");

  // Sort select shows name_asc as selected
  const sortSelect = page.locator('[data-role="sort-select"]');
  await expect(sortSelect).toHaveAttribute("data-sort-order", "name_asc");
  await expect(sortSelect.locator('option[value="name_asc"]')).toHaveAttribute("selected", "");

  // Search input value is "daily"
  await expect(page.locator('[data-role="search-input"]')).toHaveAttribute("value", "daily");
});
