import { test, expect } from "@playwright/test";

// Helper: wait for pagedjs to finish rendering
async function waitForPagedJS(page, timeout = 30000) {
  await page.waitForSelector(".pagedjs_pages", { timeout });
  await page.waitForTimeout(500);
}

// Helper: capture per-page screenshots and compare against baselines
// maxPages caps the number of pages screenshotted to keep tests fast
async function screenshotPages(page, testInfo, name, maxPages = Infinity) {
  const pages = await page.locator(".pagedjs_page").all();
  const limit = Math.min(pages.length, maxPages);
  for (let i = 0; i < limit; i++) {
    await expect(pages[i]).toHaveScreenshot(`${name}-page-${i + 1}.png`, {
      maxDiffPixelRatio: 0.01,
      timeout: 15000,
    });
  }
  return pages.length;
}

// =============================================================================
// Visual regression tests for overflow scenario fixtures
// =============================================================================

test.describe("Visual regression — overflow fixtures", () => {
  test("oversized image", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/oversized-image.html");
    await waitForPagedJS(page);
    const count = await screenshotPages(page, test.info(), "oversized-image");
    expect(count).toBeGreaterThan(0);
  });

  test("wide chart", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/wide-chart.html");
    await waitForPagedJS(page);
    const count = await screenshotPages(page, test.info(), "wide-chart");
    expect(count).toBeGreaterThan(0);
  });

  test("long table", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/long-table.html");
    await waitForPagedJS(page);
    const count = await screenshotPages(page, test.info(), "long-table");
    expect(count).toBeGreaterThan(1);
  });

  test("long code block", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/long-code.html");
    await waitForPagedJS(page);
    const count = await screenshotPages(page, test.info(), "long-code");
    expect(count).toBeGreaterThan(1);
  });

  test("orphaned heading", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/orphaned-heading.html");
    await waitForPagedJS(page);
    const count = await screenshotPages(page, test.info(), "orphaned-heading");
    expect(count).toBeGreaterThan(1);
  });
});

// =============================================================================
// Visual regression tests for Phase 3 handler behaviors
// =============================================================================

test.describe("Visual regression — Phase 3 handler fixtures", () => {
  test("blank page trigger — no blank pages visible", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/blank-page-trigger.html");
    await waitForPagedJS(page);
    const count = await screenshotPages(
      page,
      test.info(),
      "blank-page-trigger",
    );
    expect(count).toBeGreaterThan(1);
  });

  test("heading at break — heading stays with content", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/heading-at-break.html");
    await waitForPagedJS(page);
    const count = await screenshotPages(page, test.info(), "heading-at-break");
    expect(count).toBeGreaterThan(1);
  });

  test("overflowing div — overflow detected", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/overflowing-div.html");
    await waitForPagedJS(page);
    const count = await screenshotPages(page, test.info(), "overflowing-div");
    expect(count).toBeGreaterThan(0);
  });

  test("code line integrity — clean line breaks", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/code-line-integrity.html");
    await waitForPagedJS(page);
    const count = await screenshotPages(
      page,
      test.info(),
      "code-line-integrity",
    );
    expect(count).toBeGreaterThan(1);
  });
});

// =============================================================================
// Visual regression tests for generated report outputs
// =============================================================================

const TEMPLATES = [
  "basic",
  "inline",
  "finance",
  "research",
  "landscape",
  "customsize",
  "plotly",
  "greattables",
];

test.describe("Visual regression — report outputs", () => {
  // Report outputs can be large (many pages), so allow more time
  test.describe.configure({ timeout: 120_000 });

  for (const template of TEMPLATES) {
    test(template, async ({ page }) => {
      await page.goto(`/outputs/${template}.html`);
      await waitForPagedJS(page, 60000);
      // Cap at 10 pages per template to keep tests fast
      const count = await screenshotPages(
        page,
        test.info(),
        `report-${template}`,
        10,
      );
      expect(count).toBeGreaterThan(0);
    });
  }
});
