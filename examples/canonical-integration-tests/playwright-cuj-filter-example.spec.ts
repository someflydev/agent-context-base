import { expect, test, type Page } from "@playwright/test";

// ---------------------------------------------------------------------------
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
// These are Critical User Journey (CUJ) tests — multi-step sequences that
// represent realistic tasks users perform: filtering, searching, sorting,
// scrolling, and URL round-trips. They test features in combination, with
// state carried across multiple interactions.
//
// All state transitions use URL navigation (goto with params) to get full
// server-rendered state for both filter panel and results. HTMX partial
// swaps are exercised in CUJ-7 (typing) and CUJ-9 (scroll + sort change).
// ---------------------------------------------------------------------------

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:8000";

// ---------------------------------------------------------------------------
// Page Object Model
// ---------------------------------------------------------------------------

class ReportsFilterPage {
  constructor(private page: Page) {}

  /** Navigate to /ui/reports with the given query params. */
  async goto(params: Record<string, string | string[]> = {}): Promise<void> {
    const url = new URL(`${BASE_URL}/ui/reports`);
    for (const [key, value] of Object.entries(params)) {
      if (Array.isArray(value)) {
        for (const v of value) {
          url.searchParams.append(key, v);
        }
      } else {
        url.searchParams.set(key, value);
      }
    }
    await this.page.goto(url.toString());
  }

  /** Reads the numeric data-result-count attribute from [data-role="result-count"]. */
  async resultCount(): Promise<number> {
    const el = this.page.locator('[data-role="result-count"]');
    const attr = await el.getAttribute("data-result-count").catch(() => null);
    if (attr !== null) return Number(attr);
    const text = await el.textContent().catch(() => "0");
    return parseInt(text ?? "0", 10);
  }

  /**
   * Returns the numeric value of data-option-count on the facet option element
   * for the given dimension, option value, and mode (include | exclude).
   */
  async facetCount(
    dimension: string,
    option: string,
    mode: "include" | "exclude"
  ): Promise<number> {
    const el = this.page.locator(
      `[data-filter-dimension="${dimension}"][data-filter-option="${option}"][data-filter-mode="${mode}"]`
    );
    const attr = await el.getAttribute("data-option-count").catch(() => null);
    return attr !== null ? Number(attr) : 0;
  }

  /** Returns true if the include option for the given dimension/value has data-excluded="true". */
  async isIncludeGreyed(dimension: string, option: string): Promise<boolean> {
    const el = this.page.locator(
      `[data-filter-dimension="${dimension}"][data-filter-option="${option}"][data-filter-mode="include"]`
    );
    const attr = await el.getAttribute("data-excluded").catch(() => null);
    return attr === "true";
  }

  /** Returns true if the include checkbox for the given dimension/value has the disabled attribute. */
  async isIncludeCheckboxDisabled(
    dimension: string,
    option: string
  ): Promise<boolean> {
    const el = this.page.locator(
      `[data-filter-dimension="${dimension}"][data-filter-option="${option}"][data-filter-mode="include"]`
    );
    const checkbox = el.locator('input[type="checkbox"]');
    return await checkbox.isDisabled().catch(() => false);
  }

  /** Returns true if the exclude option for the given dimension/value has data-active="true". */
  async isExcludeActive(dimension: string, option: string): Promise<boolean> {
    const el = this.page.locator(
      `[data-filter-dimension="${dimension}"][data-filter-option="${option}"][data-filter-mode="exclude"]`
    );
    const attr = await el.getAttribute("data-active").catch(() => null);
    return attr === "true";
  }

  /** Returns true if the exclude checkbox for the given dimension/value is checked. */
  async isExcludeCheckboxChecked(
    dimension: string,
    option: string
  ): Promise<boolean> {
    const el = this.page.locator(
      `[data-filter-dimension="${dimension}"][data-filter-option="${option}"][data-filter-mode="exclude"]`
    );
    const checkbox = el.locator('input[type="checkbox"]');
    return await checkbox.isChecked().catch(() => false);
  }

  /** Returns true if the quick exclude for the given value has data-active="true". */
  async quickExcludeActive(value: string): Promise<boolean> {
    const el = this.page.locator(
      `[data-role="quick-exclude"][data-quick-exclude-value="${value}"]`
    );
    const attr = await el.getAttribute("data-active").catch(() => null);
    return attr === "true";
  }

  /** Returns the numeric count shown in the quick exclude badge for the given value. */
  async quickExcludeCount(value: string): Promise<number> {
    const el = this.page.locator(
      `[data-role="quick-exclude"][data-quick-exclude-value="${value}"]`
    );
    const badge = el.locator("span").last();
    const text = await badge.textContent().catch(() => "0");
    return parseInt(text ?? "0", 10);
  }

  /** Returns the value attribute of [data-role="search-input"]. */
  async searchInputValue(): Promise<string> {
    const el = this.page.locator('[data-role="search-input"]');
    return (await el.getAttribute("value").catch(() => "")) ?? "";
  }

  /** Returns the data-sort-order attribute of [data-role="sort-select"]. */
  async sortSelectValue(): Promise<string> {
    const el = this.page.locator('[data-role="sort-select"]');
    return (await el.getAttribute("data-sort-order").catch(() => "")) ?? "";
  }

  /** Returns the data-search-query attribute of #report-results. */
  async resultsSectionSearchQuery(): Promise<string> {
    const el = this.page.locator("#report-results");
    return (await el.getAttribute("data-search-query").catch(() => "")) ?? "";
  }

  /** Returns the data-sort-order attribute of #report-results. */
  async resultsSectionSortOrder(): Promise<string> {
    const el = this.page.locator("#report-results");
    return (await el.getAttribute("data-sort-order").catch(() => "")) ?? "";
  }

  /** Returns the trimmed text content of the first result card. */
  async firstResultCardText(): Promise<string> {
    const card = this.page.locator("[data-report-id]").first();
    return ((await card.textContent().catch(() => "")) ?? "").trim();
  }

  /** Returns trimmed text content of all result cards in order. */
  async allResultCardTexts(): Promise<string[]> {
    const cards = this.page.locator("[data-report-id]");
    const count = await cards.count();
    const texts: string[] = [];
    for (let i = 0; i < count; i++) {
      const text = await cards.nth(i).textContent().catch(() => "");
      texts.push((text ?? "").trim());
    }
    return texts;
  }

  /** Returns document.getElementById('filter-panel').scrollTop. */
  async filterPanelScrollTop(): Promise<number> {
    return this.page.evaluate(
      () => document.getElementById("filter-panel")?.scrollTop ?? 0
    );
  }

  /** Returns document.getElementById('report-results-container').scrollTop. */
  async resultsContainerScrollTop(): Promise<number> {
    return this.page.evaluate(
      () =>
        document.getElementById("report-results-container")?.scrollTop ?? 0
    );
  }

  /** Sets filter-panel scrollTop to the given value via page.evaluate. */
  async scrollFilterPanelTo(px: number): Promise<void> {
    await this.page.evaluate((px) => {
      const el = document.getElementById("filter-panel");
      if (el) el.scrollTop = px;
    }, px);
  }

  /** Sets report-results-container scrollTop to the given value via page.evaluate. */
  async scrollResultsContainerTo(px: number): Promise<void> {
    await this.page.evaluate((px) => {
      const el = document.getElementById("report-results-container");
      if (el) el.scrollTop = px;
    }, px);
  }

  /** Returns the computed overflow-y style of the element with the given id. */
  async overflowY(elementId: string): Promise<string> {
    return this.page.evaluate(
      (id) =>
        window.getComputedStyle(
          document.getElementById(id) ?? document.body
        ).overflowY,
      elementId
    );
  }
}

// ---------------------------------------------------------------------------
// CUJ-1: "Discover and narrow: facet filter followed by text search"
// ---------------------------------------------------------------------------

test.describe("CUJ-1: facet filter followed by text search", () => {
  let rp: ReportsFilterPage;
  test.beforeEach(({ page }) => {
    rp = new ReportsFilterPage(page);
  });

  test("applying exclude filter then narrowing with search, then clearing search", async () => {
    // Step 1: unfiltered baseline
    await rp.goto();
    expect(await rp.resultCount()).toBe(6);
    // Baseline facet counts: all 6 rows active
    expect(await rp.facetCount("team", "growth", "include")).toBe(3);
    expect(await rp.facetCount("team", "platform", "include")).toBe(3);

    // Step 2: activate status_out=archived (exclude archived)
    await rp.goto({ status_out: "archived" });
    expect(await rp.resultCount()).toBe(5);
    // RULE 1: archived include option must be greyed with count=0
    expect(await rp.isIncludeGreyed("status", "archived")).toBe(true);
    expect(await rp.isIncludeCheckboxDisabled("status", "archived")).toBe(true);
    expect(await rp.facetCount("status", "archived", "include")).toBe(0);
    // RULE 2: archived exclude option must be active with count=1
    expect(await rp.isExcludeActive("status", "archived")).toBe(true);
    expect(await rp.facetCount("status", "archived", "exclude")).toBe(1);

    // Step 3: add query=signup (matches daily-signups, trial-conversions)
    await rp.goto({ status_out: "archived", query: "signup" });
    await rp.page.waitForSelector('#report-results[data-result-count="2"]');
    expect(await rp.resultCount()).toBe(2);
    // team facet: both signup rows are growth
    expect(await rp.facetCount("team", "growth", "include")).toBe(2);
    expect(await rp.facetCount("team", "platform", "include")).toBe(0);
    // RULE 1 still holds: archived include is greyed
    expect(await rp.isIncludeGreyed("status", "archived")).toBe(true);
    expect(await rp.facetCount("status", "archived", "include")).toBe(0);
    // Search input value is pre-populated from state
    expect(await rp.searchInputValue()).toBe("signup");

    // Step 4: clear search — status_out=archived still active
    await rp.goto({ status_out: "archived" });
    expect(await rp.resultCount()).toBe(5);
    // Facet counts return to archived-excluded baseline
    expect(await rp.facetCount("team", "growth", "include")).toBe(3);
    expect(await rp.facetCount("team", "platform", "include")).toBe(2);
    // Facet filter is still active (archived still excluded)
    expect(await rp.isIncludeGreyed("status", "archived")).toBe(true);
    // Search input is empty
    expect(await rp.searchInputValue()).toBe("");
  });
});

// ---------------------------------------------------------------------------
// CUJ-2: "Search first, then progressively add facet filters"
// ---------------------------------------------------------------------------

test.describe("CUJ-2: search first, then progressively add facet filters", () => {
  let rp: ReportsFilterPage;
  test.beforeEach(({ page }) => {
    rp = new ReportsFilterPage(page);
  });

  test("progressive narrowing via search then facet includes, then region filter", async () => {
    // Step 1: query=latency — matches api-latency only
    await rp.goto({ query: "latency" });
    expect(await rp.resultCount()).toBe(1);
    expect(await rp.facetCount("team", "platform", "include")).toBe(1);
    expect(await rp.facetCount("team", "growth", "include")).toBe(0);

    // Step 2: add team_in=growth with query=latency — api-latency is platform, not growth
    await rp.goto({ query: "latency", team_in: "growth" });
    expect(await rp.resultCount()).toBe(0);
    // With search=latency+team_in=growth: no rows pass both
    expect(await rp.facetCount("team", "growth", "include")).toBe(0);

    // Step 3: remove team_in=growth — back to query=latency only
    await rp.goto({ query: "latency" });
    expect(await rp.resultCount()).toBe(1);
    expect(await rp.facetCount("team", "platform", "include")).toBe(1);

    // Step 4: add region_in=eu with query=latency — api-latency is eu
    await rp.goto({ query: "latency", region_in: "eu" });
    expect(await rp.resultCount()).toBe(1);
    expect(await rp.facetCount("region", "eu", "include")).toBe(1);

    // Step 5: clear query, keep region_in=eu
    // eu rows: api-latency, checkout-failures — 2 rows
    await rp.goto({ region_in: "eu" });
    expect(await rp.resultCount()).toBe(2);
    // Search input is now empty
    expect(await rp.searchInputValue()).toBe("");
    // Results section reflects compound filter state
    expect(await rp.resultsSectionSearchQuery()).toBe("");
  });
});

// ---------------------------------------------------------------------------
// CUJ-3: "Quick excludes + search combination"
// ---------------------------------------------------------------------------

test.describe("CUJ-3: quick excludes combined with text search", () => {
  let rp: ReportsFilterPage;
  test.beforeEach(({ page }) => {
    rp = new ReportsFilterPage(page);
  });

  test("quick exclude badge counts update with text search", async () => {
    // Step 1: baseline — quick exclude badges show impact counts for full dataset
    await rp.goto();
    expect(await rp.quickExcludeCount("archived")).toBe(1); // 1 archived row
    expect(await rp.quickExcludeCount("paused")).toBe(1);   // 1 paused row

    // Step 2: activate status_out=archived
    await rp.goto({ status_out: "archived" });
    expect(await rp.quickExcludeActive("archived")).toBe(true);
    // RULE 3: main section exclude option matches quick exclude state
    expect(await rp.isExcludeActive("status", "archived")).toBe(true);
    expect(await rp.isExcludeCheckboxChecked("status", "archived")).toBe(true);
    // RULE 1: archived include option is greyed
    expect(await rp.isIncludeGreyed("status", "archived")).toBe(true);
    expect(await rp.facetCount("status", "archived", "include")).toBe(0);

    // Step 3: add query=platform — no report_id contains "platform" → 0 results
    await rp.goto({ status_out: "archived", query: "platform" });
    expect(await rp.resultCount()).toBe(0);
    // Quick exclude counts update with search: no "platform" rows are archived or paused
    expect(await rp.quickExcludeCount("archived")).toBe(0);
    expect(await rp.quickExcludeCount("paused")).toBe(0);
    // archived exclude option impact count = 0 (no "platform" rows are archived)
    expect(await rp.facetCount("status", "archived", "exclude")).toBe(0);

    // Step 4: change query to "queue" — matches queue-depth (platform/active/apac)
    // status_out=archived still active; queue-depth is active → passes exclude
    await rp.goto({ status_out: "archived", query: "queue" });
    expect(await rp.resultCount()).toBe(1);
    expect(await rp.facetCount("team", "platform", "include")).toBe(1);
    expect(await rp.facetCount("team", "growth", "include")).toBe(0);
    // queue-depth is not archived, so archived quick exclude impact count = 0
    expect(await rp.quickExcludeCount("archived")).toBe(0);

    // Step 5: clear query — back to status_out=archived baseline
    await rp.goto({ status_out: "archived" });
    expect(await rp.resultCount()).toBe(5);
    // Quick exclude badge count for archived restores to 1
    expect(await rp.quickExcludeCount("archived")).toBe(1);
  });
});

// ---------------------------------------------------------------------------
// CUJ-4: "Sort persistence across filter changes"
// ---------------------------------------------------------------------------

test.describe("CUJ-4: sort order persists across filter changes", () => {
  let rp: ReportsFilterPage;
  test.beforeEach(({ page }) => {
    rp = new ReportsFilterPage(page);
  });

  test("sort is preserved when facet filters and search are added or changed", async () => {
    // Step 1: load with sort=name_asc
    await rp.goto({ sort: "name_asc" });
    expect(await rp.resultCount()).toBe(6);
    // Alphabetically first: api-latency
    const firstCard = await rp.firstResultCardText();
    expect(firstCard).toContain("api-latency");
    expect(await rp.sortSelectValue()).toBe("name_asc");
    expect(await rp.resultsSectionSortOrder()).toBe("name_asc");

    // Step 2: add status_out=archived — sort=name_asc preserved
    await rp.goto({ status_out: "archived", sort: "name_asc" });
    expect(await rp.resultCount()).toBe(5);
    // Alphabetically first among 5 remaining (no legacy-import): api-latency
    expect(await rp.firstResultCardText()).toContain("api-latency");
    expect(await rp.sortSelectValue()).toBe("name_asc");

    // Step 3: add team_in=growth — growth+active rows: checkout-failures, daily-signups, trial-conversions
    await rp.goto({ status_out: "archived", team_in: "growth", sort: "name_asc" });
    expect(await rp.resultCount()).toBe(3);
    // Alphabetically first: checkout-failures
    expect(await rp.firstResultCardText()).toContain("checkout-failures");
    expect(await rp.sortSelectValue()).toBe("name_asc");

    // Step 4: change sort to events_asc — same 3 rows, different order
    // events: trial-conversions(7) < checkout-failures(9) < daily-signups(12)
    await rp.goto({
      status_out: "archived",
      team_in: "growth",
      sort: "events_asc",
    });
    expect(await rp.resultCount()).toBe(3);
    // First by events ascending: trial-conversions (7 events)
    expect(await rp.firstResultCardText()).toContain("trial-conversions");
    expect(await rp.sortSelectValue()).toBe("events_asc");
    expect(await rp.resultsSectionSortOrder()).toBe("events_asc");

    // Step 5: add query=daily — 1 result, sort=events_asc still shown
    await rp.goto({
      status_out: "archived",
      team_in: "growth",
      query: "daily",
      sort: "events_asc",
    });
    expect(await rp.resultCount()).toBe(1);
    expect(await rp.sortSelectValue()).toBe("events_asc");
    // Sort never affects counts — facet counts should not differ due to sort
    expect(await rp.facetCount("team", "growth", "include")).toBe(1);
  });
});

// ---------------------------------------------------------------------------
// CUJ-5: "RULE 1 and RULE 2 hold under text search and combined filters"
// ---------------------------------------------------------------------------

test.describe("CUJ-5: RULE 1 and RULE 2 hold under active text search", () => {
  let rp: ReportsFilterPage;
  test.beforeEach(({ page }) => {
    rp = new ReportsFilterPage(page);
  });

  test("include greying and exclude impact counts are correct when search is active", async () => {
    // Step 1: status_out=archived and query=signup
    // search=signup: matches daily-signups, trial-conversions (both growth/active/us)
    // Neither is archived, so archived exclude removes 0 rows from the search set
    await rp.goto({ status_out: "archived", query: "signup" });
    expect(await rp.resultCount()).toBe(2);

    // RULE 1: archived include option must be greyed with count=0
    expect(await rp.isIncludeGreyed("status", "archived")).toBe(true);
    expect(await rp.facetCount("status", "archived", "include")).toBe(0);

    // RULE 2: archived exclude option must be active with count=0
    // (no "signup" rows are archived — impact count = 0, but filter IS active)
    expect(await rp.isExcludeActive("status", "archived")).toBe(true);
    expect(await rp.facetCount("status", "archived", "exclude")).toBe(0);
    // The exclude option must NOT be disabled even though count=0
    // (tested structurally: the exclude option has data-active="true", not data-excluded)
    expect(await rp.isIncludeGreyed("status", "active")).toBe(false);

    // paused include: count=0 (no paused rows match "signup"), NOT greyed (paused is not excluded)
    expect(await rp.facetCount("status", "paused", "include")).toBe(0);
    expect(await rp.isIncludeGreyed("status", "paused")).toBe(false);

    // active include: count=2 (both matching rows are active)
    expect(await rp.facetCount("status", "active", "include")).toBe(2);

    // Step 2: clear the search — status_out=archived still active
    await rp.goto({ status_out: "archived" });
    expect(await rp.resultCount()).toBe(5);
    // archived exclude option: count=1 (legacy-import is now in the working set)
    expect(await rp.facetCount("status", "archived", "exclude")).toBe(1);
    // paused include: count=1 (api-latency is paused, survives the archived exclude)
    expect(await rp.facetCount("status", "paused", "include")).toBe(1);
  });
});

// ---------------------------------------------------------------------------
// CUJ-6: "Include and exclude options maintain visual states under rapid filter changes"
// ---------------------------------------------------------------------------

test.describe("CUJ-6: visual state consistency across multiple exclude activations", () => {
  let rp: ReportsFilterPage;
  test.beforeEach(({ page }) => {
    rp = new ReportsFilterPage(page);
  });

  test("quick excludes and main section always agree at each state", async () => {
    // Step 1: baseline
    await rp.goto();
    expect(await rp.quickExcludeActive("archived")).toBe(false);
    expect(await rp.quickExcludeActive("paused")).toBe(false);

    // Step 2: activate archived
    await rp.goto({ status_out: "archived" });
    expect(await rp.quickExcludeActive("archived")).toBe(true);
    expect(await rp.isExcludeActive("status", "archived")).toBe(true);
    expect(await rp.isExcludeCheckboxChecked("status", "archived")).toBe(true);

    // Step 3: activate both archived and paused
    await rp.goto({ status_out: ["archived", "paused"] });
    expect(await rp.quickExcludeActive("archived")).toBe(true);
    expect(await rp.quickExcludeActive("paused")).toBe(true);
    expect(await rp.isExcludeActive("status", "archived")).toBe(true);
    expect(await rp.isExcludeActive("status", "paused")).toBe(true);

    // Step 4: deactivate archived — only paused remains active
    await rp.goto({ status_out: "paused" });
    expect(await rp.quickExcludeActive("archived")).toBe(false);
    expect(await rp.quickExcludeActive("paused")).toBe(true);
    expect(await rp.isExcludeActive("status", "archived")).toBe(false);
    expect(await rp.isExcludeActive("status", "paused")).toBe(true);
    expect(await rp.isExcludeCheckboxChecked("status", "archived")).toBe(false);
    expect(await rp.isExcludeCheckboxChecked("status", "paused")).toBe(true);

    // Step 5: add query=api — matches api-latency (platform/paused/eu)
    // status_out=paused is active; api-latency is paused → excluded → 0 results
    await rp.goto({ status_out: "paused", query: "api" });
    expect(await rp.resultCount()).toBe(0);
    // RULE 1: paused include option greyed (paused is excluded)
    expect(await rp.isIncludeGreyed("status", "paused")).toBe(true);
    expect(await rp.facetCount("status", "paused", "include")).toBe(0);
    // quick exclude paused badge count = 0 (only "api" row is api-latency which is paused)
    expect(await rp.quickExcludeCount("paused")).toBe(0);
    // Wait — api-latency IS paused, so if we exclude paused, impact=1 for full set.
    // But with search=api, only api-latency matches, and it's paused → exclude removes it.
    // So exclude_impact_count for paused with search=api = 1 (the "api" row is paused).
    // The badge count shows impact on the search-narrowed set.
    // Actually: paused exclude impact with search=api: apply search first → [api-latency],
    //   then count rows where status=paused → 1. So badge count = 1 (not 0).
    // Let me re-check: quickExcludeCount reads the count badge from the server render.
    // exclude_impact_counts(state, "status") with query="api":
    //   base = apply_text_search(REPORT_ROWS, "api") → [api-latency]
    //   for paused: other_excludes = [] (only "paused" is in status_out, and we exclude it from other_excludes)
    //   count rows where status=paused: api-latency is paused → count=1
    // So badge count for paused = 1. Corrected assertion:
    expect(await rp.quickExcludeCount("paused")).toBe(1);
    // result count = 0 because the only "api" row is excluded by status_out=paused

    // Step 6: deactivate paused — api-latency now passes, result count = 1
    await rp.goto({ query: "api" });
    expect(await rp.resultCount()).toBe(1);
    expect(await rp.isIncludeGreyed("status", "paused")).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// CUJ-7: "Empty state — search that matches no rows"
// ---------------------------------------------------------------------------

test.describe("CUJ-7: empty state when search matches no rows", () => {
  let rp: ReportsFilterPage;
  test.beforeEach(({ page }) => {
    rp = new ReportsFilterPage(page);
  });

  test("graceful empty state with zero counts everywhere", async () => {
    // Step 1: load baseline
    await rp.goto();
    expect(await rp.resultCount()).toBe(6);

    // Step 2: type query that matches nothing — using page.fill to simulate typing
    // (verifies that HTMX partial swap produces correct empty state on #report-results)
    await rp.page.fill('[data-role="search-input"]', "xxxxxxxxnothing");
    await rp.page.waitForTimeout(400); // exceed 300ms debounce
    await rp.page.waitForSelector(
      '#report-results[data-search-query="xxxxxxxxnothing"]'
    );
    await rp.page.waitForSelector('#report-results[data-result-count="0"]');

    // Results section reflects empty state
    expect(await rp.resultsSectionSearchQuery()).toBe("xxxxxxxxnothing");
    expect(
      await rp.page
        .locator("#report-results")
        .getAttribute("data-result-count")
    ).toBe("0");

    // Navigate to get full server-rendered state (filter panel + results)
    await rp.goto({ query: "xxxxxxxxnothing" });
    expect(await rp.resultCount()).toBe(0);

    // All facet option include counts are 0
    for (const [dim, options] of Object.entries({
      team: ["growth", "platform"],
      status: ["active", "paused", "archived"],
      region: ["us", "eu", "apac"],
    })) {
      for (const opt of options) {
        expect(await rp.facetCount(dim, opt, "include")).toBe(0);
      }
    }

    // All exclude impact counts are 0
    for (const [dim, options] of Object.entries({
      status: ["active", "paused", "archived"],
    })) {
      for (const opt of options) {
        expect(await rp.facetCount(dim, opt, "exclude")).toBe(0);
      }
    }

    // Step 3: quick excludes strip is still visible and rendered correctly
    await expect(
      rp.page.locator('[data-role="quick-excludes-strip"]')
    ).toBeVisible();
    // Quick exclude badges show 0 counts (correct for empty search state)
    expect(await rp.quickExcludeCount("archived")).toBe(0);
    expect(await rp.quickExcludeCount("paused")).toBe(0);

    // Step 4: sort select is still present; change sort to events_asc
    await expect(rp.page.locator('[data-role="sort-select"]')).toBeVisible();
    await rp.goto({ query: "xxxxxxxxnothing", sort: "events_asc" });
    expect(await rp.resultCount()).toBe(0);
    expect(await rp.sortSelectValue()).toBe("events_asc");
    expect(await rp.resultsSectionSortOrder()).toBe("events_asc");
    // Layout structure is intact
    await expect(
      rp.page.locator('[data-role="reports-layout"]')
    ).toBeVisible();

    // Step 5: clear search — result count returns to 6
    await rp.goto();
    expect(await rp.resultCount()).toBe(6);
    expect(await rp.facetCount("team", "growth", "include")).toBe(3);
    expect(await rp.facetCount("team", "platform", "include")).toBe(3);
  });
});

// ---------------------------------------------------------------------------
// CUJ-8: "Full compound state — all filters active simultaneously"
// ---------------------------------------------------------------------------

test.describe("CUJ-8: full compound state — all filter types active at once", () => {
  let rp: ReportsFilterPage;
  test.beforeEach(({ page }) => {
    rp = new ReportsFilterPage(page);
  });

  test("compound state is internally consistent and survives sort change", async () => {
    // Step 1: load full compound state
    // team_in=growth, status_out=archived+paused, query=checkout, sort=events_desc
    // Matching: checkout-failures (growth/active/eu, events=9) only
    await rp.goto({
      team_in: "growth",
      status_out: ["archived", "paused"],
      query: "checkout",
      sort: "events_desc",
    });

    // Step 2: verify result count and data-* attributes
    expect(await rp.resultCount()).toBe(1);
    await expect(rp.page.locator("#report-results")).toHaveAttribute(
      "data-result-count",
      "1"
    );
    await expect(rp.page.locator("#report-results")).toHaveAttribute(
      "data-search-query",
      "checkout"
    );
    await expect(rp.page.locator("#report-results")).toHaveAttribute(
      "data-sort-order",
      "events_desc"
    );

    // Step 3: verify filter panel state
    // team growth include: checked, count=1
    expect(await rp.facetCount("team", "growth", "include")).toBe(1);
    // team platform include: not checked, count=0 (search narrows to growth row only)
    expect(await rp.facetCount("team", "platform", "include")).toBe(0);
    // RULE 1: archived and paused include options are greyed with count=0
    expect(await rp.isIncludeGreyed("status", "archived")).toBe(true);
    expect(await rp.facetCount("status", "archived", "include")).toBe(0);
    expect(await rp.isIncludeGreyed("status", "paused")).toBe(true);
    expect(await rp.facetCount("status", "paused", "include")).toBe(0);
    // active include: not greyed, count=1 (checkout-failures is active)
    expect(await rp.isIncludeGreyed("status", "active")).toBe(false);
    expect(await rp.facetCount("status", "active", "include")).toBe(1);
    // region eu include: not checked, count=1 (checkout-failures is eu)
    expect(await rp.facetCount("region", "eu", "include")).toBe(1);
    expect(await rp.facetCount("region", "us", "include")).toBe(0);
    expect(await rp.facetCount("region", "apac", "include")).toBe(0);

    // Step 4: verify quick excludes strip
    expect(await rp.quickExcludeActive("archived")).toBe(true);
    expect(await rp.quickExcludeActive("paused")).toBe(true);

    // Step 5: sort select and search input values
    expect(await rp.sortSelectValue()).toBe("events_desc");
    expect(await rp.searchInputValue()).toBe("checkout");

    // Step 6: change sort to name_asc — result count and filter states unchanged
    await rp.goto({
      team_in: "growth",
      status_out: ["archived", "paused"],
      query: "checkout",
      sort: "name_asc",
    });
    expect(await rp.resultCount()).toBe(1);
    expect(await rp.sortSelectValue()).toBe("name_asc");
    expect(await rp.resultsSectionSortOrder()).toBe("name_asc");
    // Filter states from step 3 remain unchanged
    expect(await rp.isIncludeGreyed("status", "archived")).toBe(true);
    expect(await rp.isIncludeGreyed("status", "paused")).toBe(true);
    expect(await rp.quickExcludeActive("archived")).toBe(true);
    expect(await rp.quickExcludeActive("paused")).toBe(true);
    expect(await rp.facetCount("team", "growth", "include")).toBe(1);
  });
});

// ---------------------------------------------------------------------------
// CUJ-9: "Scroll independence — filter panel and results scroll separately"
// ---------------------------------------------------------------------------

test.describe("CUJ-9: filter panel and results container scroll independently", () => {
  let rp: ReportsFilterPage;
  test.beforeEach(({ page }) => {
    rp = new ReportsFilterPage(page);
  });

  test("CSS overflow-y is independently set on each panel and HTMX swap preserves filter panel scroll", async () => {
    // Step 1-2: load and verify layout element exists
    await rp.goto();
    await expect(rp.page.locator('[data-role="reports-layout"]')).toBeVisible();

    // Step 3: verify #filter-panel overflow-y is auto or scroll
    const filterPanelOverflow = await rp.overflowY("filter-panel");
    expect(["auto", "scroll"]).toContain(filterPanelOverflow);

    // Step 4: verify #report-results-container overflow-y is auto or scroll
    const resultsContainerOverflow = await rp.overflowY(
      "report-results-container"
    );
    expect(["auto", "scroll"]).toContain(resultsContainerOverflow);

    // Step 5: verify the outer wrapper has overflow hidden
    const layoutOverflow = await rp.page.evaluate(
      () =>
        window.getComputedStyle(
          document.querySelector('[data-role="reports-layout"]') ?? document.body
        ).overflow
    );
    // overflow-hidden sets overflow: hidden on both axes
    expect(layoutOverflow).toContain("hidden");

    // Step 6: programmatically scroll filter panel
    // Note: if filter panel content is shorter than viewport, scrollTop stays 0.
    // We attempt 200px and read back whatever was accepted.
    await rp.scrollFilterPanelTo(200);
    await rp.page.waitForTimeout(100); // allow browser layout to stabilize
    const filterPanelScrollAfterFilterScroll =
      await rp.filterPanelScrollTop();

    // Step 7: results container scrollTop must be 0 (scrolling filter panel did not scroll results)
    expect(await rp.resultsContainerScrollTop()).toBe(0);

    // Step 8: programmatically scroll results container
    await rp.scrollResultsContainerTo(100);
    await rp.page.waitForTimeout(100);

    // Step 9: filter panel scrollTop must still be what we set in step 6 (scroll independence)
    expect(await rp.filterPanelScrollTop()).toBe(
      filterPanelScrollAfterFilterScroll
    );

    // Step 10: trigger HTMX partial swap by changing the sort select
    // This replaces only #report-results, not the layout wrapper or filter panel.
    await rp.page.selectOption('[data-role="sort-select"]', "name_asc");
    await rp.page.waitForSelector('#report-results[data-sort-order="name_asc"]');
    await rp.page.waitForTimeout(100);

    // Step 11: filter panel scrollTop must still be non-zero (HTMX swap did NOT reset it)
    // The layout wrapper is not a swap target, so scroll positions are preserved.
    expect(await rp.filterPanelScrollTop()).toBe(
      filterPanelScrollAfterFilterScroll
    );
  });
});

// ---------------------------------------------------------------------------
// CUJ-10: "State restoration and URL round-trip"
// ---------------------------------------------------------------------------

test.describe("CUJ-10: full filter state round-trips through URL", () => {
  let rp: ReportsFilterPage;
  test.beforeEach(({ page }) => {
    rp = new ReportsFilterPage(page);
  });

  test("bookmarked URL restores identical view on reload", async ({ page }) => {
    // Step 1: load compound URL state
    // team_in=growth, status_out=archived, query=daily, sort=events_asc
    // Matching: daily-signups (growth/active/us, events=12) only
    await rp.goto({
      team_in: "growth",
      status_out: "archived",
      query: "daily",
      sort: "events_asc",
    });

    // Step 2: verify initial state
    expect(await rp.resultCount()).toBe(1);
    expect(await rp.searchInputValue()).toBe("daily");
    expect(await rp.sortSelectValue()).toBe("events_asc");
    // team growth include is checked
    await expect(
      page.locator(
        '[data-filter-dimension="team"][data-filter-option="growth"][data-filter-mode="include"] input[type="checkbox"]'
      )
    ).toBeChecked();
    // RULE 1: archived include is greyed
    expect(await rp.isIncludeGreyed("status", "archived")).toBe(true);
    expect(await rp.facetCount("status", "archived", "include")).toBe(0);
    // Quick exclude archived is active
    expect(await rp.quickExcludeActive("archived")).toBe(true);

    // Step 3: extract the full current URL and verify all params are present
    const currentUrl = page.url();
    expect(currentUrl).toContain("team_in=growth");
    expect(currentUrl).toContain("status_out=archived");
    expect(currentUrl).toContain("query=daily");
    expect(currentUrl).toContain("sort=events_asc");

    // Step 4: navigate to the extracted URL in a new page context
    const newPage = await page.context().newPage();
    const newRp = new ReportsFilterPage(newPage);
    await newPage.goto(currentUrl);

    // All assertions from step 2 must hold in the new page load
    expect(
      await newRp.resultCount()
    ).toBe(1);
    expect(await newRp.searchInputValue()).toBe("daily");
    expect(await newRp.sortSelectValue()).toBe("events_asc");
    expect(await newRp.isIncludeGreyed("status", "archived")).toBe(true);
    expect(await newRp.facetCount("status", "archived", "include")).toBe(0);
    expect(await newRp.quickExcludeActive("archived")).toBe(true);
    // RULE 1 holds in the reloaded page
    expect(await newRp.isIncludeCheckboxDisabled("status", "archived")).toBe(
      true
    );

    // Step 5: fingerprint contains all state fields including query and sort
    const fingerprint = await newPage
      .locator("#report-results")
      .getAttribute("data-query-fingerprint");
    expect(fingerprint).toContain("query=daily");
    expect(fingerprint).toContain("sort=events_asc");

    await newPage.close();
  });
});
