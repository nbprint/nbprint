import { test, expect } from "@playwright/test";

async function waitForPagedJS(page, timeout = 30000) {
  await page.waitForSelector(".pagedjs_pages", { timeout });
  await page.waitForTimeout(500);
}

// 18pt of heading spacing is 24px at 96dpi.
const SPACING_PX = 24;

test.describe("Heading spacing", () => {
  test.describe("opted in via --nbprint-heading-spacing", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/typography/heading-spacing.html");
      await waitForPagedJS(page);
    });

    test("a mid-page heading clears the cell above it", async ({ page }) => {
      const gap = await page.evaluate(() => {
        const chart = document.querySelector(
          '[data-nbprint-id="chart-above"] .chart',
        );
        const heading = document.querySelector("#midpage-heading");
        return (
          heading.getBoundingClientRect().top -
          chart.getBoundingClientRect().bottom
        );
      });
      expect(gap).toBeCloseTo(SPACING_PX, 0);
    });

    test("a page-leading heading is not indented below the page margin", async ({
      page,
    }) => {
      const offset = await page.evaluate(() => {
        const heading = document.querySelector("#pagetop-heading");
        const area = heading.closest(".pagedjs_page_content");
        return (
          heading.getBoundingClientRect().top - area.getBoundingClientRect().top
        );
      });
      expect(offset).toBeCloseTo(0, 0);
    });

    test("the trim is applied to the heading, not the wrapper", async ({
      page,
    }) => {
      const margins = await page.evaluate(() => ({
        midpage: getComputedStyle(document.querySelector("#midpage-heading"))
          .marginTop,
        pagetop: getComputedStyle(document.querySelector("#pagetop-heading"))
          .marginTop,
      }));
      expect(margins.midpage).toBe(`${SPACING_PX}px`);
      expect(margins.pagetop).toBe("0px");
    });
  });

  test("defaults to no spacing when the property is unset", async ({
    page,
  }) => {
    await page.goto("/js/tests/fixtures/overflow/orphaned-heading.html");
    await waitForPagedJS(page);

    const margins = await page.evaluate(() =>
      [
        ...document.querySelectorAll(
          ".pagedjs_page .jp-RenderedHTMLCommon :is(h1,h2,h3,h4,h5,h6):first-child",
        ),
      ].map((h) => getComputedStyle(h).marginTop),
    );

    expect(margins.length).toBeGreaterThan(0);
    for (const margin of margins) {
      expect(margin).toBe("0px");
    }
  });
});
