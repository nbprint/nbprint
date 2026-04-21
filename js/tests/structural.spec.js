import { test, expect } from "@playwright/test";

// Helper: wait for pagedjs to finish rendering
async function waitForPagedJS(page, timeout = 30000) {
  // Wait for the pagedjs_pages container to appear, which indicates rendering is complete
  await page.waitForSelector(".pagedjs_pages", { timeout });
  // Additional wait for any remaining layout
  await page.waitForTimeout(500);
}

// Helper: get all pagedjs page elements
async function getPages(page) {
  return page.locator(".pagedjs_page").all();
}

// Helper: check if a page has visible content
async function pageHasVisibleContent(pageEl) {
  const contentArea = pageEl.locator(".pagedjs_page_content");
  const children = await contentArea.locator(":scope > *").all();
  for (const child of children) {
    const box = await child.boundingBox();
    if (box && box.width > 0 && box.height > 0) {
      return true;
    }
  }
  return false;
}

test.describe("Structural assertions — overflow fixtures", () => {
  test.describe("Oversized image", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/oversized-image.html");
      await waitForPagedJS(page);
    });

    test("should render at least one page", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(0);
    });

    test("image should not overflow page width", async ({ page }) => {
      const pages = await getPages(page);
      for (const pageEl of pages) {
        const pageBox = await pageEl.boundingBox();
        const images = await pageEl.locator("img").all();
        for (const img of images) {
          const imgBox = await img.boundingBox();
          if (imgBox && pageBox) {
            expect(imgBox.x + imgBox.width).toBeLessThanOrEqual(
              pageBox.x + pageBox.width + 1,
            );
          }
        }
      }
    });

    test("image should not overflow page height", async ({ page }) => {
      const pages = await getPages(page);
      for (const pageEl of pages) {
        const pageBox = await pageEl.boundingBox();
        const images = await pageEl.locator("img").all();
        for (const img of images) {
          const imgBox = await img.boundingBox();
          if (imgBox && pageBox) {
            expect(imgBox.y + imgBox.height).toBeLessThanOrEqual(
              pageBox.y + pageBox.height + 1,
            );
          }
        }
      }
    });

    test("no blank pages", async ({ page }) => {
      const pages = await getPages(page);
      for (let i = 0; i < pages.length; i++) {
        const hasContent = await pageHasVisibleContent(pages[i]);
        expect(hasContent, `Page ${i + 1} should have visible content`).toBe(
          true,
        );
      }
    });
  });

  test.describe("Wide chart", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/wide-chart.html");
      await waitForPagedJS(page);
    });

    test("should render at least one page", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(0);
    });

    test("SVG should not overflow page width", async ({ page }) => {
      const pages = await getPages(page);
      for (const pageEl of pages) {
        const pageBox = await pageEl.boundingBox();
        const svgs = await pageEl.locator("svg").all();
        for (const svg of svgs) {
          const svgBox = await svg.boundingBox();
          if (svgBox && pageBox) {
            expect(svgBox.x + svgBox.width).toBeLessThanOrEqual(
              pageBox.x + pageBox.width + 1,
            );
          }
        }
      }
    });

    test("no blank pages", async ({ page }) => {
      const pages = await getPages(page);
      for (let i = 0; i < pages.length; i++) {
        const hasContent = await pageHasVisibleContent(pages[i]);
        expect(hasContent, `Page ${i + 1} should have visible content`).toBe(
          true,
        );
      }
    });
  });

  test.describe("Long table", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/long-table.html");
      await waitForPagedJS(page);
    });

    test("should span multiple pages", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(1);
    });

    test("table rows should not be split across pages", async ({ page }) => {
      // Check that no <tr> straddles a page boundary by verifying
      // each row fits within its page's bounding box
      const pages = await getPages(page);
      for (const pageEl of pages) {
        const pageBox = await pageEl.boundingBox();
        const rows = await pageEl.locator("tr").all();
        for (const row of rows) {
          const rowBox = await row.boundingBox();
          if (rowBox && pageBox) {
            expect(rowBox.y + rowBox.height).toBeLessThanOrEqual(
              pageBox.y + pageBox.height + 1,
            );
          }
        }
      }
    });

    test("no blank pages", async ({ page }) => {
      const pages = await getPages(page);
      for (let i = 0; i < pages.length; i++) {
        const hasContent = await pageHasVisibleContent(pages[i]);
        expect(hasContent, `Page ${i + 1} should have visible content`).toBe(
          true,
        );
      }
    });
  });

  test.describe("Long code block", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/long-code.html");
      await waitForPagedJS(page);
    });

    test("should span multiple pages", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(1);
    });

    test("no blank pages", async ({ page }) => {
      const pages = await getPages(page);
      for (let i = 0; i < pages.length; i++) {
        const hasContent = await pageHasVisibleContent(pages[i]);
        expect(hasContent, `Page ${i + 1} should have visible content`).toBe(
          true,
        );
      }
    });
  });

  test.describe("Orphaned heading", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/orphaned-heading.html");
      await waitForPagedJS(page);
    });

    test("should render multiple pages", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(1);
    });

    test("headings should not be the last element on a page", async ({
      page,
    }) => {
      const pages = await getPages(page);
      for (let i = 0; i < pages.length; i++) {
        // Skip the last page — a heading at the end of the last page is fine
        if (i === pages.length - 1) continue;

        const pageBox = await pages[i].boundingBox();
        if (!pageBox) continue;

        // Find all headings on this page
        const headings = await pages[i].locator("h1, h2, h3, h4, h5, h6").all();

        for (const heading of headings) {
          const headingBox = await heading.boundingBox();
          if (!headingBox) continue;

          // Check if this heading is near the bottom of the page
          // (within the last 5% of page height)
          const threshold = pageBox.y + pageBox.height * 0.95;
          if (headingBox.y > threshold) {
            // If the heading is near the bottom, there should be
            // substantive content after it on the same page
            const nextSibling = await heading.evaluate((el) => {
              let next = el.nextElementSibling;
              while (next) {
                if (
                  next.tagName &&
                  !next.tagName.match(/^H[1-6]$/) &&
                  next.textContent.trim().length > 0
                ) {
                  return true;
                }
                next = next.nextElementSibling;
              }
              return false;
            });
            expect(
              nextSibling,
              `Heading on page ${i + 1} appears orphaned at the bottom`,
            ).toBe(true);
          }
        }
      }
    });

    test("no blank pages", async ({ page }) => {
      const pages = await getPages(page);
      for (let i = 0; i < pages.length; i++) {
        const hasContent = await pageHasVisibleContent(pages[i]);
        expect(hasContent, `Page ${i + 1} should have visible content`).toBe(
          true,
        );
      }
    });
  });
});

test.describe("Pre-pagination preprocessing", () => {
  test("preprocessing attribute is set on content root", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/oversized-image.html");
    await waitForPagedJS(page);
    const attr = await page
      .locator("main")
      .first()
      .getAttribute("data-nbprint-preprocessed");
    expect(attr).toBe("true");
  });

  test("oversized image gets max-height constrained", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/oversized-image.html");
    await waitForPagedJS(page);
    // The 3000px tall image should have been constrained by preprocessing
    // Verify that after pagination, the image fits within its page
    const pages = await getPages(page);
    for (const pageEl of pages) {
      const pageBox = await pageEl.boundingBox();
      const images = await pageEl.locator("img").all();
      for (const img of images) {
        const imgBox = await img.boundingBox();
        if (imgBox && pageBox) {
          expect(imgBox.height).toBeLessThanOrEqual(pageBox.height + 1);
        }
      }
    }
  });

  test("wide SVG gets scaled down to fit page width", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/wide-chart.html");
    await waitForPagedJS(page);
    const pages = await getPages(page);
    for (const pageEl of pages) {
      const pageBox = await pageEl.boundingBox();
      const svgs = await pageEl.locator("svg").all();
      for (const svg of svgs) {
        const svgBox = await svg.boundingBox();
        if (svgBox && pageBox) {
          expect(svgBox.width).toBeLessThanOrEqual(pageBox.width + 1);
        }
      }
    }
  });

  test("tall table gets data-nbprint-paginate attribute", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/long-table.html");
    await waitForPagedJS(page);
    // The original table was >1 page tall, so it should have been annotated.
    // After pagedjs splits it, fragments may exist — check that the attribute
    // was set on at least one table element.
    const annotated = await page.evaluate(() => {
      const tables = document.querySelectorAll("table");
      return Array.from(tables).some(
        (t) => t.getAttribute("data-nbprint-paginate") === "table",
      );
    });
    expect(annotated).toBe(true);
  });
});

test.describe("Phase 3 — Paged.js handler hooks", () => {
  test("3.1: no overflow attributes on well-fitting fixtures", async ({
    page,
  }) => {
    await page.goto("/js/tests/fixtures/overflow/oversized-image.html");
    await waitForPagedJS(page);
    // Phase 2 scaling + Phase 3 overflow handler should mean no overflow
    const overflowed = await page.evaluate(() => {
      return document.querySelectorAll("[data-nbprint-overflow]").length;
    });
    expect(overflowed).toBe(0);
  });

  test("3.2: pages with content are not marked blank", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/long-table.html");
    await waitForPagedJS(page);
    const pages = await getPages(page);
    for (let i = 0; i < pages.length; i++) {
      const isBlank = await pages[i].getAttribute("data-nbprint-blank");
      expect(isBlank, `Page ${i + 1} should not be marked blank`).toBeNull();
    }
  });

  test("3.4: long code block has line-wrapped spans", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/long-code.html");
    await waitForPagedJS(page);
    // Code lines should be wrapped in spans for line-aware splitting
    const hasLineSpans = await page.evaluate(() => {
      const pres = document.querySelectorAll("pre");
      for (const pre of pres) {
        const spans = pre.querySelectorAll('span[style*="break-inside"]');
        if (spans.length > 0) return true;
      }
      return false;
    });
    expect(hasLineSpans).toBe(true);
  });

  test("3.5: headings near page bottom have content following them", async ({
    page,
  }) => {
    await page.goto("/js/tests/fixtures/overflow/orphaned-heading.html");
    await waitForPagedJS(page);
    // The keep-with-next hook should prevent headings from being orphaned.
    // Verify no heading appears at the very bottom of a page without
    // subsequent content on the same page.
    const pages = await getPages(page);
    for (let i = 0; i < pages.length - 1; i++) {
      const pageBox = await pages[i].boundingBox();
      if (!pageBox) continue;

      const headings = await pages[i].locator("h1, h2, h3, h4, h5, h6").all();
      for (const heading of headings) {
        const headingBox = await heading.boundingBox();
        if (!headingBox) continue;

        // Check bottom 3% of page — a heading there with no following
        // content is orphaned
        const threshold = pageBox.y + pageBox.height * 0.97;
        if (headingBox.y + headingBox.height > threshold) {
          const hasNext = await heading.evaluate((el) => {
            let next = el.nextElementSibling;
            while (next) {
              if (
                next.tagName &&
                !next.tagName.match(/^H[1-6]$/) &&
                next.getBoundingClientRect().height > 0
              ) {
                return true;
              }
              next = next.nextElementSibling;
            }
            return false;
          });
          expect(
            hasNext,
            `Heading on page ${i + 1} appears orphaned at bottom`,
          ).toBe(true);
        }
      }
    }
  });
});

test.describe("Phase 3 — targeted fixture assertions", () => {
  test.describe("Blank page trigger", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/blank-page-trigger.html");
      await waitForPagedJS(page);
    });

    test("should render multiple pages", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(1);
    });

    test("blank pages are detected and marked", async ({ page }) => {
      // If any blank pages exist, they should be marked
      const pages = await getPages(page);
      for (let i = 0; i < pages.length; i++) {
        const isBlank = await pages[i].getAttribute("data-nbprint-blank");
        const hasContent = await pageHasVisibleContent(pages[i]);
        if (isBlank === "true") {
          // If marked blank, verify it really has no visible content
          expect(
            hasContent,
            `Page ${i + 1} marked blank but has visible content`,
          ).toBe(false);
        }
        if (hasContent) {
          // If it has content, it should not be marked blank
          expect(
            isBlank,
            `Page ${i + 1} has content but is marked blank`,
          ).toBeNull();
        }
      }
    });
  });

  test.describe("Heading at page break", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/heading-at-break.html");
      await waitForPagedJS(page);
    });

    test("should render multiple pages", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(1);
    });

    test("no heading is the last visible element on a non-final page", async ({
      page,
    }) => {
      const pages = await getPages(page);
      for (let i = 0; i < pages.length - 1; i++) {
        const pageBox = await pages[i].boundingBox();
        if (!pageBox) continue;

        const headings = await pages[i].locator("h1, h2, h3, h4, h5, h6").all();
        for (const heading of headings) {
          const headingBox = await heading.boundingBox();
          if (!headingBox) continue;

          // If heading is in the bottom 5% of the page
          const threshold = pageBox.y + pageBox.height * 0.95;
          if (headingBox.y > threshold) {
            const hasFollowing = await heading.evaluate((el) => {
              let next = el.nextElementSibling;
              while (next) {
                if (
                  next.tagName &&
                  !next.tagName.match(/^H[1-6]$/) &&
                  next.textContent.trim().length > 0
                ) {
                  return true;
                }
                next = next.nextElementSibling;
              }
              return false;
            });
            expect(
              hasFollowing,
              `Heading "${await heading.textContent()}" on page ${i + 1} appears orphaned`,
            ).toBe(true);
          }
        }
      }
    });

    test("each h2 appears on same page as its first paragraph", async ({
      page,
    }) => {
      // For each h2, verify the very next <p> sibling is on the same page
      const pages = await getPages(page);
      for (let i = 0; i < pages.length; i++) {
        const headings = await pages[i].locator("h2").all();
        for (const heading of headings) {
          const headingBox = await heading.boundingBox();
          if (!headingBox) continue;

          // Find the next paragraph on the same page
          const nextP = await heading.evaluate((el) => {
            let next = el.nextElementSibling;
            while (next) {
              if (next.tagName === "P") {
                const rect = next.getBoundingClientRect();
                return { y: rect.y, height: rect.height };
              }
              next = next.nextElementSibling;
            }
            return null;
          });

          if (nextP && nextP.height > 0) {
            const pageBox = await pages[i].boundingBox();
            // The paragraph should be on the same page as the heading
            expect(nextP.y).toBeLessThan(pageBox.y + pageBox.height);
          }
        }
      }
    });
  });

  test.describe("Overflowing div", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/overflowing-div.html");
      await waitForPagedJS(page);
    });

    test("should render at least one page", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(0);
    });

    test("wide div is tagged with data-nbprint-overflow", async ({ page }) => {
      const overflowed = await page.evaluate(() => {
        return document.querySelectorAll("[data-nbprint-overflow]").length;
      });
      expect(overflowed).toBeGreaterThan(0);
    });
  });

  test.describe("Code line integrity", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/code-line-integrity.html");
      await waitForPagedJS(page);
    });

    test("should span multiple pages", async ({ page }) => {
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(1);
    });

    test("code lines are wrapped for break control", async ({ page }) => {
      const lineCount = await page.evaluate(() => {
        const spans = document.querySelectorAll(
          'pre span[style*="break-inside"]',
        );
        return spans.length;
      });
      expect(lineCount).toBeGreaterThan(10);
    });

    test("no blank pages", async ({ page }) => {
      const pages = await getPages(page);
      for (let i = 0; i < pages.length; i++) {
        const hasContent = await pageHasVisibleContent(pages[i]);
        expect(hasContent, `Page ${i + 1} should have visible content`).toBe(
          true,
        );
      }
    });
  });
});
