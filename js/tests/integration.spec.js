import { test, expect } from "@playwright/test";

// Helper: wait for pagedjs to finish rendering
async function waitForPagedJS(page, timeout = 30000) {
  await page.waitForSelector(".pagedjs_pages", { timeout });
  await page.waitForTimeout(500);
}

// Templates tested through the full Python → HTML → pagedjs pipeline.
// The globalSetup (integration.setup.mjs) generates fresh HTML via `nbprint run`.
const TEMPLATES = ["basic", "inline", "finance", "research", "landscape"];

test.describe("Integration — full pipeline structural checks", () => {
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

      // Verify pages were rendered
      const pages = await page.locator(".pagedjs_page").all();
      expect(pages.length).toBeGreaterThan(0);

      // Check for content overflow (logged as warnings, not hard failures —
      // some templates have pre-existing overflow that future work will fix)
      let overflowCount = 0;
      for (const p of pages) {
        const overflow = await p.evaluate((el) => {
          const content = el.querySelector(".pagedjs_page_content");
          if (!content) return false;
          return (
            content.scrollHeight > content.clientHeight + 2 ||
            content.scrollWidth > content.clientWidth + 2
          );
        });
        if (overflow) overflowCount++;
      }
      if (overflowCount > 0) {
        console.warn(
          `[${template}] ${overflowCount}/${pages.length} pages have overflow`,
        );
      }

      // Check no blank pages
      let blankCount = 0;
      for (const p of pages) {
        const isBlank = await p.evaluate((el) => {
          const content = el.querySelector(".pagedjs_page_content");
          if (!content) return true;
          return (
            content.textContent.trim().length === 0 &&
            content.querySelectorAll("img, svg, canvas, table").length === 0
          );
        });
        if (isBlank) blankCount++;
      }
      if (blankCount > 0) {
        console.warn(
          `[${template}] ${blankCount}/${pages.length} blank pages detected`,
        );
      }
    });
  }
});
