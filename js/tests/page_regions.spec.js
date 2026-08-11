import { test, expect } from "@playwright/test";

async function waitForPagedJS(page, timeout = 30000) {
  await page.waitForSelector(".pagedjs_pages", { timeout });
  await page.waitForTimeout(500);
}

test.describe("Page regions", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/js/tests/fixtures/page_regions/running-element.html");
    await waitForPagedJS(page);
  });

  test("the document paginates onto more than one page", async ({ page }) => {
    expect(await page.locator(".pagedjs_page").count()).toBeGreaterThan(1);
  });

  test("body carries the pagedjs marker the unpaginated-hiding rule keys off", async ({
    page,
  }) => {
    await expect(page.locator("body")).toHaveClass(/\bpagedjs\b/);
  });

  test("the running element is lifted into a bottom-left margin box", async ({
    page,
  }) => {
    const placed = await page.evaluate(
      () =>
        [...document.querySelectorAll(".footer-logo")].filter((el) =>
          el.closest(".pagedjs_margin-bottom-left"),
        ).length,
    );
    expect(placed).toBeGreaterThan(0);
  });

  test("the source element does not stay visible in the content flow", async ({
    page,
  }) => {
    const leaked = await page.evaluate(() =>
      [...document.querySelectorAll(".footer-logo")]
        .filter((el) => el.closest(".pagedjs_page_content"))
        .map((el) => getComputedStyle(el).display),
    );
    expect(leaked.every((display) => display === "none")).toBe(true);
  });

  test("margin boxes are hidden on the first page", async ({ page }) => {
    const visible = await page.evaluate(() => {
      const first = document.querySelector(".pagedjs_page");
      return [...first.querySelectorAll(".pagedjs_margin-bottom")].map(
        (el) => getComputedStyle(el).display,
      );
    });
    expect(visible.length).toBeGreaterThan(0);
    for (const display of visible) {
      expect(display).toBe("none");
    }
  });

  test("margin boxes still render on later pages", async ({ page }) => {
    const displays = await page.evaluate(() => {
      const pages = [...document.querySelectorAll(".pagedjs_page")];
      const later = pages[1];
      return [...later.querySelectorAll(".pagedjs_margin-bottom")].map(
        (el) => getComputedStyle(el).display,
      );
    });
    expect(displays.length).toBeGreaterThan(0);
    expect(displays.some((d) => d !== "none")).toBe(true);
  });

  test("the page counter region is unaffected", async ({ page }) => {
    const text = await page.evaluate(() => {
      const pages = [...document.querySelectorAll(".pagedjs_page")];
      const el = pages[1].querySelector(
        ".pagedjs_margin-bottom-center .pagedjs_margin-content",
      );
      return el ? getComputedStyle(el, "::after").content : null;
    });
    expect(text).not.toBeNull();
  });
});
