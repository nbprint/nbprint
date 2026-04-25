import { test, expect } from "@playwright/test";

// Helper: wait for pagedjs to finish rendering.
async function waitForPagedJS(page, timeout = 30000) {
  await page.waitForSelector(".pagedjs_pages", { timeout });
  await page.waitForTimeout(500);
}

async function getPages(page) {
  return page.locator(".pagedjs_page").all();
}

test.describe("ContentPageBlock — Phase 9.3", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/js/tests/fixtures/page_block/basic.html");
    await waitForPagedJS(page);
  });

  test("renders at least one page", async ({ page }) => {
    const pages = await getPages(page);
    expect(pages.length).toBeGreaterThan(0);
  });

  test("data-nbprint-block attribute survives pagination", async ({ page }) => {
    // Paged.js clones source content into pagedjs_page_content; assert the
    // attribute appears in the rendered DOM.
    const blocks = await page.locator("[data-nbprint-block]").all();
    expect(blocks.length).toBeGreaterThanOrEqual(3);
  });

  test("default block carries break-inside: avoid", async ({ page }) => {
    const block = page.locator('[data-nbprint-block="block-default"]').first();
    const breakInside = await block.evaluate(
      (el) => getComputedStyle(el).breakInside,
    );
    expect(breakInside).toBe("avoid");
  });

  test("spanned block reflects data-nbprint-span", async ({ page }) => {
    const block = page.locator('[data-nbprint-block="block-spanned"]').first();
    const span = await block.getAttribute("data-nbprint-span");
    expect(span).toBe("2");
  });

  test("aspect block applies aspect-ratio", async ({ page }) => {
    const block = page.locator('[data-nbprint-block="block-aspect"]').first();
    const aspect = await block.evaluate(
      (el) => getComputedStyle(el).aspectRatio,
    );
    // Browsers normalize "16/9" to "16 / 9".
    expect(aspect.replace(/\s+/g, "")).toBe("16/9");
  });

  test("blocks do not overflow page width", async ({ page }) => {
    const pages = await getPages(page);
    for (const pageEl of pages) {
      const pageBox = await pageEl.boundingBox();
      const blocks = await pageEl.locator("[data-nbprint-block]").all();
      for (const block of blocks) {
        const box = await block.boundingBox();
        if (box && pageBox) {
          expect(box.x + box.width).toBeLessThanOrEqual(
            pageBox.x + pageBox.width + 1,
          );
        }
      }
    }
  });
});
