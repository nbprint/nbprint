import { test, expect } from "@playwright/test";

// Helper: wait for pagedjs to finish rendering
async function waitForPagedJS(page, timeout = 30000) {
  await page.waitForSelector(".pagedjs_pages", { timeout });
  await page.waitForTimeout(500);
}

// Helper: capture per-page screenshots and compare against baselines
async function screenshotPages(page, name, maxPages = 10) {
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

// Templates tested through the full Python → HTML → pagedjs pipeline.
// The globalSetup (integration.setup.mjs) generates fresh HTML via `nbprint run`.
const TEMPLATES = ["basic", "inline", "finance", "research", "landscape"];

test.describe("Integration — full pipeline visual regression", () => {
  test.describe.configure({ timeout: 120_000 });

  for (const template of TEMPLATES) {
    test(template, async ({ page }) => {
      // Try loading the HTML output; skip if not generated
      const response = await page.goto(`/outputs/${template}.html`);
      if (!response || response.status() === 404) {
        test.skip(true, `${template}.html not found — was it generated?`);
        return;
      }

      await waitForPagedJS(page, 60000);
      const count = await screenshotPages(page, `integration-${template}`, 10);
      expect(count).toBeGreaterThan(0);
    });
  }
});
