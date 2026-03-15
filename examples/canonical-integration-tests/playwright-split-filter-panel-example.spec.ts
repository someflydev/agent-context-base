import { expect, test } from "@playwright/test";

// Dataset reference (from fastapi-split-filter-panel-example.py):
//   daily-signups     growth   active   us
//   trial-conversions growth   active   us
//   api-latency       platform paused   eu
//   checkout-failures growth   active   eu
//   queue-depth       platform active   apac
//   legacy-import     platform archived us

test("include option for excluded value shows count 0 and is greyed out", async ({ page }) => {
  await page.goto("/ui/reports?status_out=archived");

  const includeOpt = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="archived"][data-filter-mode="include"]'
  );
  // RULE 1: count must be 0
  await expect(includeOpt).toHaveAttribute("data-option-count", "0");
  // RULE 1: data-excluded must be present
  await expect(includeOpt).toHaveAttribute("data-excluded", "true");
  // RULE 1: checkbox must be disabled
  await expect(includeOpt.locator('input[type="checkbox"]')).toBeDisabled();
  // RULE 1: label must carry greyed-out classes
  await expect(includeOpt).toHaveClass(/opacity-50/);
  await expect(includeOpt).toHaveClass(/cursor-not-allowed/);
  // RULE 1: visible count text is "0"
  await expect(includeOpt.locator('[data-role="option-count"]')).toHaveText("0");
});

test("exclude option for excluded value shows non-zero impact count", async ({ page }) => {
  await page.goto("/ui/reports?status_out=archived");

  const excludeOpt = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="archived"][data-filter-mode="exclude"]'
  );
  // RULE 2: data-active must be present
  await expect(excludeOpt).toHaveAttribute("data-active", "true");
  // RULE 2: count must not be 0 — archived has 1 row (legacy-import)
  const countAttr = await excludeOpt.getAttribute("data-option-count");
  expect(countAttr).not.toBe("0");
  expect(Number(countAttr)).toBeGreaterThan(0);
  // RULE 2: checkbox must be checked
  await expect(excludeOpt.locator('input[type="checkbox"]')).toBeChecked();
  // RULE 2: visible count badge is "1"
  await expect(excludeOpt.locator('[data-role="option-count"]')).toHaveText("1");
});

test("non-excluded values are not greyed out", async ({ page }) => {
  await page.goto("/ui/reports?status_out=archived");

  const includeActive = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="active"][data-filter-mode="include"]'
  );
  // data-excluded must be absent
  await expect(includeActive).not.toHaveAttribute("data-excluded", "true");
  // checkbox must not be disabled
  await expect(includeActive.locator('input[type="checkbox"]')).not.toBeDisabled();
  // count should be 4 (active rows: daily-signups, trial-conversions, checkout-failures, queue-depth)
  await expect(includeActive).toHaveAttribute("data-option-count", "4");
});

test("active quick exclude reflects in main section as checked", async ({ page }) => {
  await page.goto("/ui/reports?status_out=archived");

  // RULE 3: quick exclude toggle is active
  const qeToggle = page.locator(
    '[data-role="quick-exclude"][data-quick-exclude-value="archived"]'
  );
  await expect(qeToggle).toHaveAttribute("data-active", "true");

  // RULE 3b: main section exclude option is also active and checked
  const mainExclude = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="archived"][data-filter-mode="exclude"]'
  );
  await expect(mainExclude).toHaveAttribute("data-active", "true");
  await expect(mainExclude.locator('input[type="checkbox"]')).toBeChecked();
});

test("inactive quick exclude is unchecked in both strip and main section", async ({ page }) => {
  await page.goto("/ui/reports");

  // Quick exclude toggle for archived must not be active
  const qeToggle = page.locator(
    '[data-role="quick-exclude"][data-quick-exclude-value="archived"]'
  );
  const activeAttr = await qeToggle.getAttribute("data-active");
  expect(activeAttr).not.toBe("true");

  // Main section exclude for archived must not be checked
  const mainExclude = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="archived"][data-filter-mode="exclude"]'
  );
  await expect(mainExclude).not.toHaveAttribute("data-active", "true");
  await expect(mainExclude.locator('input[type="checkbox"]')).not.toBeChecked();

  // Include option for archived must not be greyed out
  const includeArchived = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="archived"][data-filter-mode="include"]'
  );
  await expect(includeArchived).not.toHaveAttribute("data-excluded", "true");
  await expect(includeArchived.locator('input[type="checkbox"]')).not.toBeDisabled();
});

test("exclude impact count for paused is correct with partial filters active", async ({ page }) => {
  // team_in=platform filters to: api-latency(paused), queue-depth(active), legacy-import(archived)
  // exclude_impact_counts for status="paused" = rows where team=platform AND status=paused
  // = api-latency only → count = 1
  await page.goto("/ui/reports?team_in=platform");

  const pausedExclude = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="paused"][data-filter-mode="exclude"]'
  );
  await expect(pausedExclude).toHaveAttribute("data-option-count", "1");
  await expect(pausedExclude.locator('[data-role="option-count"]')).toHaveText("1");
});

test("multiple quick excludes active simultaneously", async ({ page }) => {
  await page.goto("/ui/reports?status_out=archived&status_out=paused");

  // Both quick exclude toggles are active
  await expect(
    page.locator('[data-role="quick-exclude"][data-quick-exclude-value="archived"]')
  ).toHaveAttribute("data-active", "true");
  await expect(
    page.locator('[data-role="quick-exclude"][data-quick-exclude-value="paused"]')
  ).toHaveAttribute("data-active", "true");

  // Both main-section exclude options are active and checked
  const archivedExclude = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="archived"][data-filter-mode="exclude"]'
  );
  await expect(archivedExclude).toHaveAttribute("data-active", "true");
  await expect(archivedExclude.locator('input[type="checkbox"]')).toBeChecked();

  const pausedExclude = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="paused"][data-filter-mode="exclude"]'
  );
  await expect(pausedExclude).toHaveAttribute("data-active", "true");
  await expect(pausedExclude.locator('input[type="checkbox"]')).toBeChecked();

  // Include options for excluded values are greyed and zeroed
  const archivedInclude = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="archived"][data-filter-mode="include"]'
  );
  await expect(archivedInclude).toHaveAttribute("data-excluded", "true");
  await expect(archivedInclude).toHaveAttribute("data-option-count", "0");

  const pausedInclude = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="paused"][data-filter-mode="include"]'
  );
  await expect(pausedInclude).toHaveAttribute("data-excluded", "true");
  await expect(pausedInclude).toHaveAttribute("data-option-count", "0");

  // Include option for "active" is NOT greyed and count > 0
  const activeInclude = page.locator(
    '[data-filter-dimension="status"] [data-filter-option="active"][data-filter-mode="include"]'
  );
  await expect(activeInclude).not.toHaveAttribute("data-excluded", "true");
  await expect(activeInclude.locator('input[type="checkbox"]')).not.toBeDisabled();
  const activeCount = await activeInclude.getAttribute("data-option-count");
  expect(Number(activeCount)).toBeGreaterThan(0);
});
