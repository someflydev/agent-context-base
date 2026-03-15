import { expect, test } from "@playwright/test";

test("backend-driven filtering keeps rows, count, and chart payload aligned", async ({ page, request }) => {
  await page.goto("/ui/reports?status_out=archived");

  await page
    .locator('[data-filter-dimension="team"] [data-filter-option="growth"][data-filter-mode="include"] input[type="checkbox"]')
    .check();

  await expect(page.locator('[data-role="result-count"]')).toHaveText("3 results");
  await expect(page.locator('[data-report-id]')).toHaveCount(3);
  await expect(page.locator('[data-report-id="legacy-import"]')).toHaveCount(0);
  await expect(page.locator('[data-role="active-filters"]')).toContainText("status not archived");

  const chartResponse = await request.get("/api/reports/chart?team_in=growth&status_out=archived");
  expect(chartResponse.ok()).toBeTruthy();

  const chart = await chartResponse.json();
  expect(chart.result_count).toBe(3);
  expect(chart.filters).toEqual({
    team_in: ["growth"],
    team_out: [],
    status_in: [],
    status_out: ["archived"],
    region_in: [],
    region_out: [],
  });
  expect(chart.totals.events).toBe(28);
  expect(chart.plotly.data[0].x).toEqual(["2026-03-01", "2026-03-02", "2026-03-03"]);
});
