import { test, expect } from "@playwright/test";

const PAGE_CONTENT_HEIGHT = 960; // US Letter (1056px) minus 0.5in margins

async function waitForPagedJS(page, timeout = 30000) {
  await page.waitForSelector(".pagedjs_pages", { timeout });
  await page.waitForTimeout(500);
}

/**
 * Navigate to a fit fixture, collecting console warnings from before the
 * first byte so the render-time overflow warning cannot be missed.
 */
async function loadFixture(page, name) {
  const warnings = [];
  page.on("console", (msg) => {
    if (msg.type() === "warning") warnings.push(msg.text());
  });
  await page.goto(`/js/tests/fixtures/page_box_fit/${name}.html`);
  await waitForPagedJS(page);
  return warnings;
}

function renderedBox(page, id) {
  return page.locator(`.pagedjs_pages [data-nbprint-page-box="${id}"]`).first();
}

/** Heights of every page-box block as actually rendered, in document order. */
async function renderedBlockHeights(page) {
  return page.evaluate(() =>
    Array.from(
      document.querySelectorAll(".pagedjs_pages [data-nbprint-block]"),
    ).map((el) => el.getBoundingClientRect().height),
  );
}

const sum = (values) => values.reduce((a, b) => a + b, 0);

test.describe("ContentPageBox fit", () => {
  test.describe('fit="scale" within the floor', () => {
    // 3 x 350px = 1050px of content on a 960px page.
    const REQUIRED_SCALE = PAGE_CONTENT_HEIGHT / 1050;

    test("records the scale it applied", async ({ page }) => {
      await loadFixture(page, "fit-scale");
      const applied = await renderedBox(page, "box-fit-scale").getAttribute(
        "data-nbprint-fit-scale",
      );
      expect(parseFloat(applied)).toBeCloseTo(REQUIRED_SCALE, 2);
    });

    test("blocks render at the scaled size", async ({ page }) => {
      await loadFixture(page, "fit-scale");
      const heights = await renderedBlockHeights(page);
      expect(heights).toHaveLength(3);
      for (const height of heights) {
        expect(height).toBeCloseTo(350 * REQUIRED_SCALE, 0);
      }
    });

    test("the composite now fits one page", async ({ page }) => {
      await loadFixture(page, "fit-scale");
      const heights = await renderedBlockHeights(page);
      expect(sum(heights)).toBeLessThanOrEqual(PAGE_CONTENT_HEIGHT + 1);
      // ...and it did have to be scaled to get there.
      expect(sum(heights)).toBeGreaterThan(PAGE_CONTENT_HEIGHT - 5);
    });

    test("does not flag an overflow", async ({ page }) => {
      const warnings = await loadFixture(page, "fit-scale");
      await expect(renderedBox(page, "box-fit-scale")).not.toHaveAttribute(
        "data-nbprint-fit-overflow",
      );
      expect(warnings.filter((w) => w.includes("overflows its page"))).toEqual(
        [],
      );
    });
  });

  test.describe('fit="scale" past the floor', () => {
    // 4 x 400px = 1600px needs 0.6; "scale" stops at 0.75.
    test("clamps at the floor rather than scaling further", async ({
      page,
    }) => {
      await loadFixture(page, "fit-scale-clamped");
      const applied = await renderedBox(page, "box-fit-clamped").getAttribute(
        "data-nbprint-fit-scale",
      );
      expect(parseFloat(applied)).toBeCloseTo(0.75, 3);
      const heights = await renderedBlockHeights(page);
      for (const height of heights) {
        expect(height).toBeCloseTo(300, 0);
      }
    });

    test("flags and warns because it still overflows", async ({ page }) => {
      const warnings = await loadFixture(page, "fit-scale-clamped");
      await expect(renderedBox(page, "box-fit-clamped")).toHaveAttribute(
        "data-nbprint-fit-overflow",
        "true",
      );
      expect(
        warnings.some(
          (w) =>
            w.includes("box-fit-clamped") && w.includes("overflows its page"),
        ),
      ).toBe(true);
      const heights = await renderedBlockHeights(page);
      expect(sum(heights)).toBeGreaterThan(PAGE_CONTENT_HEIGHT);
    });
  });

  test.describe('fit="shrink"', () => {
    // Identical content to fit-scale-clamped; the tighter floor reaches 0.6.
    test("goes further than scale would", async ({ page }) => {
      await loadFixture(page, "fit-shrink");
      const applied = await renderedBox(page, "box-fit-shrink").getAttribute(
        "data-nbprint-fit-scale",
      );
      expect(parseFloat(applied)).toBeCloseTo(0.6, 2);
      expect(parseFloat(applied)).toBeLessThan(0.75);
    });

    test("the composite fits one page", async ({ page }) => {
      const warnings = await loadFixture(page, "fit-shrink");
      const heights = await renderedBlockHeights(page);
      expect(heights).toHaveLength(4);
      for (const height of heights) {
        expect(height).toBeCloseTo(240, 0);
      }
      expect(sum(heights)).toBeLessThanOrEqual(PAGE_CONTENT_HEIGHT + 1);
      await expect(renderedBox(page, "box-fit-shrink")).not.toHaveAttribute(
        "data-nbprint-fit-overflow",
      );
      expect(warnings.filter((w) => w.includes("overflows its page"))).toEqual(
        [],
      );
    });
  });

  test.describe('fit="strict"', () => {
    test("leaves every block at its authored size", async ({ page }) => {
      await loadFixture(page, "fit-strict");
      await expect(renderedBox(page, "box-fit-strict")).not.toHaveAttribute(
        "data-nbprint-fit-scale",
      );
      const heights = await renderedBlockHeights(page);
      expect(heights).toHaveLength(4);
      for (const height of heights) {
        expect(height).toBeCloseTo(400, 0);
      }
      expect(sum(heights)).toBeGreaterThan(PAGE_CONTENT_HEIGHT);
    });

    test("warns loudly with the measured geometry", async ({ page }) => {
      const warnings = await loadFixture(page, "fit-strict");
      await expect(renderedBox(page, "box-fit-strict")).toHaveAttribute(
        "data-nbprint-fit-overflow",
        "true",
      );
      const overflow = warnings.find((w) => w.includes("box-fit-strict"));
      expect(overflow).toBeDefined();
      expect(overflow).toContain('fit="strict"');
      expect(overflow).toContain("1600px");
      expect(overflow).toContain("960px");
    });
  });

  test.describe('fit="none"', () => {
    test("is left completely alone", async ({ page }) => {
      const warnings = await loadFixture(page, "fit-none");
      const box = renderedBox(page, "box-fit-none");
      await expect(box).not.toHaveAttribute("data-nbprint-fit-scale");
      await expect(box).not.toHaveAttribute("data-nbprint-fit-overflow");
      const heights = await renderedBlockHeights(page);
      for (const height of heights) {
        expect(height).toBeCloseTo(400, 0);
      }
      expect(warnings.filter((w) => w.includes("overflows its page"))).toEqual(
        [],
      );
    });
  });

  test("oversized images stay capped to their container", async ({ page }) => {
    // The composite pass must not undo the per-image max-width cap: a
    // page-box column is narrower than the page, and an image that escapes
    // it overlaps its neighbour.
    await page.goto(
      "/js/tests/fixtures/overflow/oversized-image-in-columns.html",
    );
    await waitForPagedJS(page);
    const images = await page.evaluate(() =>
      Array.from(document.querySelectorAll("img")).map((img) => ({
        rendered: Math.round(img.getBoundingClientRect().width),
        container: Math.round(img.parentElement.getBoundingClientRect().width),
        maxWidth: img.style.maxWidth,
      })),
    );
    expect(images.length).toBeGreaterThan(0);
    for (const { rendered, container, maxWidth } of images) {
      expect(maxWidth).toContain("min(100%");
      expect(rendered).toBeLessThanOrEqual(container + 1);
    }
  });
});
