import { test, expect } from "@playwright/test";

async function waitForPagedJS(page, timeout = 30000) {
  await page.waitForSelector(".pagedjs_pages", { timeout });
  await page.waitForTimeout(500);
}

async function getPages(page) {
  return page.locator(".pagedjs_page").all();
}

test.describe("ContentPageBox layout presets — Phase 9.4", () => {
  test.describe("layout=columns-2", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/page_box/columns-2.html");
      await waitForPagedJS(page);
    });

    test("renders at least one page", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(0);
    });

    test("page-box reflects layout attribute", async ({ page }) => {
      const box = page.locator('[data-nbprint-page-box="box-cols"]').first();
      await expect(box).toHaveAttribute("data-nbprint-layout", "columns-2");
    });

    test("computed column-count is 2", async ({ page }) => {
      const box = page.locator('[data-nbprint-page-box="box-cols"]').first();
      const count = await box.evaluate(
        (el) => getComputedStyle(el).columnCount,
      );
      expect(count).toBe("2");
    });

    test("blocks survive pagination with break-inside avoid", async ({
      page,
    }) => {
      const blocks = await page.locator("[data-nbprint-block]").all();
      expect(blocks.length).toBeGreaterThanOrEqual(4);
      for (const block of blocks) {
        const breakInside = await block.evaluate(
          (el) => getComputedStyle(el).breakInside,
        );
        expect(breakInside).toBe("avoid");
      }
    });
  });

  test.describe("layout=grid-2x2", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/page_box/grid-2x2.html");
      await waitForPagedJS(page);
    });

    test("renders at least one page", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(0);
    });

    test("page-box uses display: grid", async ({ page }) => {
      const box = page.locator('[data-nbprint-page-box="box-grid"]').first();
      const display = await box.evaluate((el) => getComputedStyle(el).display);
      expect(display).toBe("grid");
    });

    test("grid-template-columns has two equal tracks", async ({ page }) => {
      const box = page.locator('[data-nbprint-page-box="box-grid"]').first();
      const tracks = await box.evaluate(
        (el) => getComputedStyle(el).gridTemplateColumns,
      );
      // Browsers resolve "repeat(2, 1fr)" to two pixel widths separated
      // by a space — assert exactly two tokens.
      expect(tracks.split(/\s+/).filter(Boolean).length).toBe(2);
    });

    test("spanned block occupies both columns", async ({ page }) => {
      const spanned = page.locator('[data-nbprint-block="g3"]').first();
      const span = await spanned.getAttribute("data-nbprint-span");
      expect(span).toBe("2");
      // Width should be (roughly) the same as the page-box's content area,
      // i.e. wider than its non-spanning siblings.
      const spannedBox = await spanned.boundingBox();
      const sibling = page.locator('[data-nbprint-block="g1"]').first();
      const siblingBox = await sibling.boundingBox();
      expect(spannedBox.width).toBeGreaterThan(siblingBox.width * 1.5);
    });
  });

  test.describe("layout=grid + grid_template (named areas)", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/page_box/named-areas.html");
      await waitForPagedJS(page);
    });

    test("renders at least one page", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(0);
    });

    test("hero area spans the full width", async ({ page }) => {
      const hero = page.locator('[data-nbprint-block="b-hero"]').first();
      const chart = page.locator('[data-nbprint-block="b-chart"]').first();
      const heroBox = await hero.boundingBox();
      const chartBox = await chart.boundingBox();
      // Hero area covers both columns -> roughly 2x the chart width.
      expect(heroBox.width).toBeGreaterThan(chartBox.width * 1.5);
    });

    test("chart and table sit side by side", async ({ page }) => {
      const chart = page.locator('[data-nbprint-block="b-chart"]').first();
      const table = page.locator('[data-nbprint-block="b-table"]').first();
      const chartBox = await chart.boundingBox();
      const tableBox = await table.boundingBox();
      // Same row → similar y, table is to the right of chart.
      expect(Math.abs(chartBox.y - tableBox.y)).toBeLessThan(5);
      expect(tableBox.x).toBeGreaterThan(chartBox.x);
    });

    test("data-nbprint-area attributes survive pagination", async ({
      page,
    }) => {
      for (const area of ["hero", "chart", "table"]) {
        const el = page.locator(`[data-nbprint-area="${area}"]`).first();
        await expect(el).toHaveAttribute("data-nbprint-area", area);
      }
    });
  });
});
