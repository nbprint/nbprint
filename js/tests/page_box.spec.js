import { test, expect } from "@playwright/test";

async function waitForPagedJS(page, timeout = 30000) {
  await page.waitForSelector(".pagedjs_pages", { timeout });
  await page.waitForTimeout(500);
}

async function getPages(page) {
  return page.locator(".pagedjs_page").all();
}

function renderedBlock(page, id) {
  return page.locator(`.pagedjs_pages [data-nbprint-block="${id}"]`).first();
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

    test("columns start on the same visual baseline", async ({ page }) => {
      const firstColumn = await renderedBlock(page, "b1").boundingBox();
      const secondColumn = await renderedBlock(page, "b3").boundingBox();
      expect(Math.abs(firstColumn.y - secondColumn.y)).toBeLessThan(2);
    });

    test("visual regression", async ({ page }) => {
      await expect(page).toHaveScreenshot("layout-columns-2.png", {
        fullPage: true,
      });
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

    test("visual regression", async ({ page }) => {
      await expect(page).toHaveScreenshot("layout-grid-2x2.png", {
        fullPage: true,
      });
    });
  });

  test.describe("layout=flow", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/page_box/flow.html");
      await waitForPagedJS(page);
    });

    test("renders at least one page", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(0);
    });

    test("page-box reflects layout attribute", async ({ page }) => {
      const box = page.locator('[data-nbprint-page-box="box-flow"]').first();
      await expect(box).toHaveAttribute("data-nbprint-layout", "flow");
    });

    test("page-box uses display: block", async ({ page }) => {
      const box = page.locator('[data-nbprint-page-box="box-flow"]').first();
      const display = await box.evaluate((el) => getComputedStyle(el).display);
      expect(display).toBe("block");
    });

    test("blocks stack vertically with gap", async ({ page }) => {
      const b1 = page.locator('[data-nbprint-block="f1"]').first();
      const b2 = page.locator('[data-nbprint-block="f2"]').first();
      const box1 = await b1.boundingBox();
      const box2 = await b2.boundingBox();
      // b2 starts below b1
      expect(box2.y).toBeGreaterThan(box1.y + box1.height - 1);
    });

    test("visual regression", async ({ page }) => {
      await expect(page).toHaveScreenshot("layout-flow.png", {
        fullPage: true,
      });
    });
  });

  test.describe("layout=flex-row", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/page_box/flex-row.html");
      await waitForPagedJS(page);
    });

    test("renders at least one page", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(0);
    });

    test("page-box reflects layout attribute", async ({ page }) => {
      const box = page.locator('[data-nbprint-page-box="box-flexrow"]').first();
      await expect(box).toHaveAttribute("data-nbprint-layout", "flex-row");
    });

    test("page-box uses display: flex with row direction", async ({ page }) => {
      const box = page.locator('[data-nbprint-page-box="box-flexrow"]').first();
      const display = await box.evaluate((el) => getComputedStyle(el).display);
      expect(display).toBe("flex");
      const direction = await box.evaluate(
        (el) => getComputedStyle(el).flexDirection,
      );
      expect(direction).toBe("row");
    });

    test("blocks sit side by side", async ({ page }) => {
      const fr1 = page.locator('[data-nbprint-block="fr1"]').first();
      const fr2 = page.locator('[data-nbprint-block="fr2"]').first();
      const fr3 = page.locator('[data-nbprint-block="fr3"]').first();
      const box1 = await fr1.boundingBox();
      const box2 = await fr2.boundingBox();
      const box3 = await fr3.boundingBox();
      // Same row: similar y, increasing x
      expect(Math.abs(box1.y - box2.y)).toBeLessThan(5);
      expect(box2.x).toBeGreaterThan(box1.x);
      expect(box3.x).toBeGreaterThan(box2.x);
    });

    test("visual regression", async ({ page }) => {
      await expect(page).toHaveScreenshot("layout-flex-row.png", {
        fullPage: true,
      });
    });
  });

  test.describe("layout=flex-column", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/page_box/flex-column.html");
      await waitForPagedJS(page);
    });

    test("renders at least one page", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(0);
    });

    test("page-box uses display: flex with column direction", async ({
      page,
    }) => {
      const box = page.locator('[data-nbprint-page-box="box-flexcol"]').first();
      const display = await box.evaluate((el) => getComputedStyle(el).display);
      expect(display).toBe("flex");
      const direction = await box.evaluate(
        (el) => getComputedStyle(el).flexDirection,
      );
      expect(direction).toBe("column");
    });

    test("blocks stack vertically", async ({ page }) => {
      const fc1 = page.locator('[data-nbprint-block="fc1"]').first();
      const fc2 = page.locator('[data-nbprint-block="fc2"]').first();
      const box1 = await fc1.boundingBox();
      const box2 = await fc2.boundingBox();
      expect(box2.y).toBeGreaterThan(box1.y + box1.height - 1);
    });

    test("visual regression", async ({ page }) => {
      await expect(page).toHaveScreenshot("layout-flex-column.png", {
        fullPage: true,
      });
    });
  });

  test.describe("layout=columns-3", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/page_box/columns-3.html");
      await waitForPagedJS(page);
    });

    test("renders at least one page", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(0);
    });

    test("computed column-count is 3", async ({ page }) => {
      const box = page.locator('[data-nbprint-page-box="box-cols3"]').first();
      const count = await box.evaluate(
        (el) => getComputedStyle(el).columnCount,
      );
      expect(count).toBe("3");
    });

    test("six blocks survive pagination", async ({ page }) => {
      const blocks = await page.locator("[data-nbprint-block]").all();
      expect(blocks.length).toBeGreaterThanOrEqual(6);
    });

    test("columns start on the same visual baseline", async ({ page }) => {
      const firstColumn = await renderedBlock(page, "c1").boundingBox();
      const secondColumn = await renderedBlock(page, "c3").boundingBox();
      const thirdColumn = await renderedBlock(page, "c5").boundingBox();
      expect(Math.abs(firstColumn.y - secondColumn.y)).toBeLessThan(2);
      expect(Math.abs(firstColumn.y - thirdColumn.y)).toBeLessThan(2);
    });

    test("visual regression", async ({ page }) => {
      await expect(page).toHaveScreenshot("layout-columns-3.png", {
        fullPage: true,
      });
    });
  });

  test.describe("layout=grid-3x3", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/page_box/grid-3x3.html");
      await waitForPagedJS(page);
    });

    test("renders at least one page", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(0);
    });

    test("page-box uses display: grid", async ({ page }) => {
      const box = page.locator('[data-nbprint-page-box="box-grid33"]').first();
      const display = await box.evaluate((el) => getComputedStyle(el).display);
      expect(display).toBe("grid");
    });

    test("grid-template-columns has three equal tracks", async ({ page }) => {
      const box = page.locator('[data-nbprint-page-box="box-grid33"]').first();
      const tracks = await box.evaluate(
        (el) => getComputedStyle(el).gridTemplateColumns,
      );
      expect(tracks.split(/\s+/).filter(Boolean).length).toBe(3);
    });

    test("nine blocks present", async ({ page }) => {
      const blocks = await page.locator("[data-nbprint-block]").all();
      expect(blocks.length).toBe(9);
    });

    test("visual regression", async ({ page }) => {
      await expect(page).toHaveScreenshot("layout-grid-3x3.png", {
        fullPage: true,
      });
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

    test("visual regression", async ({ page }) => {
      await expect(page).toHaveScreenshot("layout-named-areas.png", {
        fullPage: true,
      });
    });
  });
});
