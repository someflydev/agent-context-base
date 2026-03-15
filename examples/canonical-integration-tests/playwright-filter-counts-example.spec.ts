import { expect, test } from "@playwright/test";

test("filter option counts reflect backend facet semantics", async ({ page }) => {
  await page.goto("/ui/reports?team_in=growth&status_out=archived");

  const teamFacet = page.locator('[data-filter-dimension="team"]');
  await expect(teamFacet.locator('[data-filter-option="growth"][data-filter-mode="include"] [data-role="option-count"]')).toHaveText("3");
  await expect(teamFacet.locator('[data-filter-option="platform"][data-filter-mode="include"] [data-role="option-count"]')).toHaveText("2");

  const regionFacet = page.locator('[data-filter-dimension="region"]');
  await expect(regionFacet.locator('[data-filter-option="us"][data-filter-mode="include"] [data-role="option-count"]')).toHaveText("2");
  await expect(regionFacet.locator('[data-filter-option="eu"][data-filter-mode="include"] [data-role="option-count"]')).toHaveText("1");
  await expect(regionFacet.locator('[data-filter-option="apac"][data-filter-mode="include"] [data-role="option-count"]')).toHaveText("0");

  await expect(page.locator('[data-role="result-count"]')).toHaveAttribute("data-result-count", "3");
  await expect(page.locator('[data-role="count-discipline"]')).toContainText("backend query semantics");
});
