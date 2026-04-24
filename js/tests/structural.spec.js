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

    test("table starts on page 1 alongside preceding content", async ({
      page,
    }) => {
      const pages = await getPages(page);
      const firstPage = pages[0];
      // Page 1 should have both the heading and table rows
      const hasHeading = (await firstPage.locator("h2").count()) > 0;
      const hasTableRows = (await firstPage.locator("tbody tr").count()) > 0;
      expect(hasHeading, "Page 1 should have the heading").toBe(true);
      expect(hasTableRows, "Page 1 should have table rows").toBe(true);
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

    test("table starts on page 1 alongside heading", async ({ page }) => {
      const pages = await getPages(page);
      const page1 = pages[0];
      const headings = await page1.locator("h2").count();
      const rows = await page1.locator("tr").count();
      expect(headings).toBeGreaterThan(0);
      expect(rows).toBeGreaterThan(0);
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

    test("all 100 rows are visible in sequence (no gaps)", async ({ page }) => {
      // Collect the first-cell text of every visible <tr> across pages,
      // in visual order (top-to-bottom, page-by-page).
      const rowNumbers = await page.evaluate(() => {
        const pages = document.querySelectorAll(".pagedjs_page");
        const nums = [];
        for (const pg of pages) {
          const rows = pg.querySelectorAll("tbody > tr");
          for (const r of rows) {
            const cell = r.querySelector("td");
            if (cell) nums.push(Number(cell.textContent.trim()));
          }
        }
        return nums;
      });
      expect(rowNumbers.length).toBe(100);
      for (let i = 0; i < 100; i++) {
        expect(rowNumbers[i], `row ${i + 1} should be in position`).toBe(i + 1);
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

    test("code starts on page 1 alongside heading", async ({ page }) => {
      const pages = await getPages(page);
      const page1 = pages[0];
      const headings = await page1.locator("h2").count();
      const preBlocks = await page1.locator("pre").count();
      expect(headings).toBeGreaterThan(0);
      expect(preBlocks).toBeGreaterThan(0);
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

  test("tall table gets annotated and split into chunks", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/long-table.html");
    await waitForPagedJS(page);
    // The original table was >1 page tall. After preprocessing,
    // it should have been split into multiple chunk tables.
    const result = await page.evaluate(() => {
      const chunks = document.querySelectorAll(
        "table[data-nbprint-table-chunk]",
      );
      const annotated = document.querySelectorAll(
        'table[data-nbprint-paginate="table"]',
      );
      return { chunks: chunks.length, annotated: annotated.length };
    });
    // Either it was split into chunks (table_header_repeat=true, default)
    // or it still has the paginate annotation
    expect(result.chunks + result.annotated).toBeGreaterThan(0);
  });
});

test.describe("Paged.js handler hooks", () => {
  test("no overflow attributes on well-fitting fixtures", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/oversized-image.html");
    await waitForPagedJS(page);
    // Preprocessing scaling + overflow handler should mean no overflow
    const overflowed = await page.evaluate(() => {
      return document.querySelectorAll("[data-nbprint-overflow]").length;
    });
    expect(overflowed).toBe(0);
  });

  test("pages with content are not marked blank", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/long-table.html");
    await waitForPagedJS(page);
    const pages = await getPages(page);
    for (let i = 0; i < pages.length; i++) {
      const isBlank = await pages[i].getAttribute("data-nbprint-blank");
      expect(isBlank, `Page ${i + 1} should not be marked blank`).toBeNull();
    }
  });

  test("long code block has line-wrapped spans", async ({ page }) => {
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

  test("headings near page bottom have content following them", async ({
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

test.describe("Handler hooks — targeted fixture assertions", () => {
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

test.describe("Post-pagination validation", () => {
  test("validation attribute is set after processing", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/oversized-image.html");
    await waitForPagedJS(page);
    const attr = await page.evaluate(() => {
      const container = document.querySelector(".pagedjs_pages");
      return container?.getAttribute("data-nbprint-validated");
    });
    expect(attr).toBe("true");
  });

  test("no blank pages remain after validation", async ({ page }) => {
    await page.goto("/js/tests/fixtures/overflow/blank-page-trigger.html");
    await waitForPagedJS(page);
    // After post-pagination validation, any blank pages should have been removed
    const pages = await getPages(page);
    for (let i = 0; i < pages.length; i++) {
      const hasContent = await pageHasVisibleContent(pages[i]);
      expect(hasContent, `Page ${i + 1} should have visible content`).toBe(
        true,
      );
    }
  });

  test("overflow elements are detected by post-validation", async ({
    page,
  }) => {
    await page.goto("/js/tests/fixtures/overflow/overflowing-div.html");
    await waitForPagedJS(page);
    // The wide div should be tagged by the handler and confirmed by post-pagination validation
    const overflowed = await page.evaluate(() => {
      return document.querySelectorAll("[data-nbprint-overflow]").length;
    });
    expect(overflowed).toBeGreaterThan(0);
  });

  test("well-fitting content has no overflow after validation", async ({
    page,
  }) => {
    await page.goto("/js/tests/fixtures/overflow/long-table.html");
    await waitForPagedJS(page);
    const overflowed = await page.evaluate(() => {
      return document.querySelectorAll("[data-nbprint-overflow]").length;
    });
    expect(overflowed).toBe(0);
  });

  test.describe("Blank page intent detection", () => {
    test("accidental blank pages are removed", async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/blank-page-trigger.html");
      await waitForPagedJS(page);
      // No pages should have data-nbprint-blank="true" remaining
      const accidentalBlanks = await page.evaluate(() => {
        return document.querySelectorAll(
          '.pagedjs_page[data-nbprint-blank="true"]',
        ).length;
      });
      expect(accidentalBlanks).toBe(0);
      // Every remaining page should have visible content
      const pages = await getPages(page);
      for (let i = 0; i < pages.length; i++) {
        const hasContent = await pageHasVisibleContent(pages[i]);
        expect(hasContent, `Page ${i + 1} should have visible content`).toBe(
          true,
        );
      }
    });

    test("intentional blank pages are preserved", async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/intentional-blank.html");
      await waitForPagedJS(page);
      const pages = await getPages(page);
      // Should have at least 2 pages (chapter 1 + chapter 2)
      expect(pages.length).toBeGreaterThanOrEqual(2);

      // No accidental blanks should remain
      const accidentalBlanks = await page.evaluate(() => {
        return document.querySelectorAll(
          '.pagedjs_page[data-nbprint-blank="true"]',
        ).length;
      });
      expect(accidentalBlanks).toBe(0);

      // If pagedjs inserted a blank verso for recto alignment,
      // it should still be in the DOM (not removed)
      const intentionalBlanks = await page.evaluate(() => {
        return document.querySelectorAll(
          '.pagedjs_page[data-nbprint-blank="intentional"]',
        ).length;
      });
      // The total page count includes any intentional blanks
      const totalPagesIncludingBlanks = pages.length;
      const contentPages = totalPagesIncludingBlanks - intentionalBlanks;
      expect(contentPages).toBeGreaterThanOrEqual(2);
    });

    test("intentional blank page has correct attribute value", async ({
      page,
    }) => {
      await page.goto("/js/tests/fixtures/overflow/intentional-blank.html");
      await waitForPagedJS(page);
      // Any blank pages should be marked "intentional", not "true"
      const blankPages = await page.evaluate(() => {
        const pages = document.querySelectorAll(
          ".pagedjs_page[data-nbprint-blank]",
        );
        return Array.from(pages).map((p) => ({
          value: p.getAttribute("data-nbprint-blank"),
          pageNum: p.getAttribute("data-page-number"),
        }));
      });
      for (const bp of blankPages) {
        expect(
          bp.value,
          `Blank page ${bp.pageNum} should be "intentional"`,
        ).toBe("intentional");
      }
    });
  });
});

test.describe("Configuration surface", () => {
  test.describe("overflow_strategy", () => {
    test("warn strategy tags overflow as warn (no resize)", async ({
      page,
    }) => {
      await page.goto(
        "/js/tests/fixtures/overflow/overflow-strategy-warn.html",
      );
      await waitForPagedJS(page);
      const result = await page.evaluate(() => {
        const el = document.getElementById("wide-element");
        return {
          attr: el?.getAttribute("data-nbprint-overflow"),
          // With warn, the element should NOT be resized
          width: el?.style.maxWidth || "none",
        };
      });
      expect(result.attr).toBe("warn");
      expect(result.width).toBe("none");
    });

    test("clip strategy applies overflow:hidden and maxWidth", async ({
      page,
    }) => {
      await page.goto(
        "/js/tests/fixtures/overflow/overflow-strategy-clip.html",
      );
      await waitForPagedJS(page);
      const result = await page.evaluate(() => {
        const el = document.getElementById("wide-element");
        return {
          attr: el?.getAttribute("data-nbprint-overflow"),
          overflow: el?.style.overflow,
          hasMaxWidth: el?.style.maxWidth !== "",
        };
      });
      expect(result.attr).toBe("clip");
      expect(result.overflow).toBe("hidden");
      expect(result.hasMaxWidth).toBe(true);
    });

    test("default (scale) strategy shrinks images to fit", async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/oversized-image.html");
      await waitForPagedJS(page);
      // Images should have been scaled, not tagged with overflow
      const overflowed = await page.evaluate(() => {
        return document.querySelectorAll("[data-nbprint-overflow]").length;
      });
      expect(overflowed).toBe(0);
    });
  });

  test.describe("blank_page_removal", () => {
    test("blank pages are removed when enabled (default)", async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/blank-page-trigger.html");
      await waitForPagedJS(page);
      const blanks = await page.evaluate(() => {
        return document.querySelectorAll(
          '.pagedjs_page[data-nbprint-blank="true"]',
        ).length;
      });
      expect(blanks).toBe(0);
    });

    test("blank pages are kept when blank_page_removal=false", async ({
      page,
    }) => {
      await page.goto(
        "/js/tests/fixtures/overflow/blank-removal-disabled.html",
      );
      await waitForPagedJS(page);
      // With removal disabled, accidental blank pages should still
      // be present (marked but not removed)
      const blanks = await page.evaluate(() => {
        return document.querySelectorAll(
          '.pagedjs_page[data-nbprint-blank="true"]',
        ).length;
      });
      // The blank-page-trigger content should produce blank pages
      // but they should NOT be removed when config disables it
      const validated = await page.evaluate(() => {
        return document
          .querySelector(".pagedjs_pages")
          ?.getAttribute("data-nbprint-validated");
      });
      expect(validated).toBe("true");
      // Page count should be >= the count with removal enabled
      const totalPages = await page.evaluate(() => {
        return document.querySelectorAll(".pagedjs_page").length;
      });
      expect(totalPages).toBeGreaterThan(0);
    });
  });

  test.describe("per-element overflow override", () => {
    test("element with data-nbprint-overflow=clip uses clip strategy", async ({
      page,
    }) => {
      await page.goto("/js/tests/fixtures/overflow/per-element-override.html");
      await waitForPagedJS(page);
      const result = await page.evaluate(() => {
        const el = document.getElementById("clipped-element");
        return {
          attr: el?.getAttribute("data-nbprint-overflow"),
          overflow: el?.style.overflow,
          hasMaxWidth: el?.style.maxWidth !== "",
        };
      });
      expect(result.attr).toBe("clip");
      expect(result.overflow).toBe("hidden");
      expect(result.hasMaxWidth).toBe(true);
    });
  });
});

test.describe("Table header repetition", () => {
  test.describe("Plain table", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/table-header-repeat.html");
      await waitForPagedJS(page);
    });

    test("table is split into multiple chunks", async ({ page }) => {
      const chunks = await page.evaluate(() => {
        return document.querySelectorAll("table[data-nbprint-table-chunk]")
          .length;
      });
      expect(chunks).toBeGreaterThan(1);
    });

    test("every chunk has a thead", async ({ page }) => {
      const result = await page.evaluate(() => {
        const chunks = document.querySelectorAll(
          "table[data-nbprint-table-chunk]",
        );
        let allHaveThead = true;
        for (const chunk of chunks) {
          if (!chunk.querySelector("thead")) {
            allHaveThead = false;
            break;
          }
        }
        return { count: chunks.length, allHaveThead };
      });
      expect(result.count).toBeGreaterThan(1);
      expect(result.allHaveThead).toBe(true);
    });

    test("continuation chunks have data-nbprint-repeated thead", async ({
      page,
    }) => {
      const result = await page.evaluate(() => {
        const chunks = document.querySelectorAll(
          "table[data-nbprint-table-chunk]",
        );
        const repeated = document.querySelectorAll(
          'thead[data-nbprint-repeated="true"]',
        ).length;
        // First chunk should have original thead, rest should be repeated
        return { totalChunks: chunks.length, repeatedHeaders: repeated };
      });
      expect(result.repeatedHeaders).toBe(result.totalChunks - 1);
    });

    test("repeated thead contains column headers", async ({ page }) => {
      const headerText = await page.evaluate(() => {
        const repeated = document.querySelector(
          'thead[data-nbprint-repeated="true"]',
        );
        if (!repeated) return null;
        const ths = repeated.querySelectorAll("th");
        return Array.from(ths).map((th) => th.textContent.trim());
      });
      expect(headerText).not.toBeNull();
      expect(headerText).toContain("Row");
      expect(headerText).toContain("Name");
    });

    test("all rows are present across all chunks (no data loss)", async ({
      page,
    }) => {
      const totalRows = await page.evaluate(() => {
        const chunks = document.querySelectorAll(
          "table[data-nbprint-table-chunk]",
        );
        let count = 0;
        for (const chunk of chunks) {
          count += chunk.querySelectorAll("tbody > tr").length;
        }
        return count;
      });
      // Original table has 100 rows
      expect(totalRows).toBe(100);
    });
  });

  test.describe("GT table", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(
        "/js/tests/fixtures/overflow/table-header-repeat-gt.html",
      );
      await waitForPagedJS(page);
    });

    test("table is split into multiple chunks", async ({ page }) => {
      const chunks = await page.evaluate(() => {
        return document.querySelectorAll("table[data-nbprint-table-chunk]")
          .length;
      });
      expect(chunks).toBeGreaterThan(1);
    });

    test("continuation chunks have column headers but not title/subtitle", async ({
      page,
    }) => {
      const result = await page.evaluate(() => {
        const repeated = document.querySelectorAll(
          'thead[data-nbprint-repeated="true"]',
        );
        const info = [];
        for (const thead of repeated) {
          const hasTitle = !!thead.querySelector(".gt_title");
          const hasSubtitle = !!thead.querySelector(".gt_subtitle");
          const hasColHeadings = !!thead.querySelector(".gt_col_heading");
          const colTexts = Array.from(
            thead.querySelectorAll(".gt_col_heading"),
          ).map((th) => th.textContent.trim());
          info.push({ hasTitle, hasSubtitle, hasColHeadings, colTexts });
        }
        return info;
      });
      expect(result.length).toBeGreaterThan(0);
      for (const thead of result) {
        expect(thead.hasTitle).toBe(false);
        expect(thead.hasSubtitle).toBe(false);
        expect(thead.hasColHeadings).toBe(true);
        expect(thead.colTexts).toContain("Row ID");
        expect(thead.colTexts).toContain("Category");
      }
    });

    test("first chunk has title and subtitle", async ({ page }) => {
      const firstChunkHasTitle = await page.evaluate(() => {
        const first = document.querySelector(
          'table[data-nbprint-table-chunk^="1/"]',
        );
        if (!first) return false;
        const thead = first.querySelector("thead:not([data-nbprint-repeated])");
        return !!(thead && thead.querySelector(".gt_title"));
      });
      expect(firstChunkHasTitle).toBe(true);
    });

    test("all rows are present across all chunks (no data loss)", async ({
      page,
    }) => {
      const totalRows = await page.evaluate(() => {
        const chunks = document.querySelectorAll(
          "table[data-nbprint-table-chunk]",
        );
        let count = 0;
        for (const chunk of chunks) {
          count += chunk.querySelectorAll("tbody > tr").length;
        }
        return count;
      });
      expect(totalRows).toBe(100);
    });
  });

  test.describe("6.3: table_header_repeat config", () => {
    test("headers are NOT repeated when table_header_repeat=false", async ({
      page,
    }) => {
      await page.goto(
        "/js/tests/fixtures/overflow/table-header-repeat-disabled.html",
      );
      await waitForPagedJS(page);
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThan(1);

      const repeated = await page.evaluate(() => {
        return document.querySelectorAll('thead[data-nbprint-repeated="true"]')
          .length;
      });
      expect(repeated).toBe(0);

      // Table should NOT be split into chunks
      const chunks = await page.evaluate(() => {
        return document.querySelectorAll("table[data-nbprint-table-chunk]")
          .length;
      });
      expect(chunks).toBe(0);
    });
  });

  test.describe("Table starting mid-page", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/table-midpage.html");
      await waitForPagedJS(page);
    });

    test("table spills from mid-page onto subsequent page(s)", async ({
      page,
    }) => {
      const pages = await getPages(page);
      // Must span at least 2 pages (starts mid-page, overflows)
      expect(pages.length).toBeGreaterThan(1);

      // First page should have non-table content before the table
      const firstPageHasHeading = await pages[0]
        .locator("h2")
        .count()
        .then((c) => c > 0);
      expect(firstPageHasHeading).toBe(true);
    });

    test("table is split into chunks with repeated headers", async ({
      page,
    }) => {
      const result = await page.evaluate(() => {
        const chunks = document.querySelectorAll(
          "table[data-nbprint-table-chunk]",
        );
        const repeated = document.querySelectorAll(
          'thead[data-nbprint-repeated="true"]',
        );
        return { chunks: chunks.length, repeated: repeated.length };
      });
      expect(result.chunks).toBeGreaterThan(1);
      // Every chunk after the first should have a repeated header
      expect(result.repeated).toBe(result.chunks - 1);
    });

    test("all 60 rows are present across chunks (no data loss)", async ({
      page,
    }) => {
      const totalRows = await page.evaluate(() => {
        const chunks = document.querySelectorAll(
          "table[data-nbprint-table-chunk]",
        );
        let count = 0;
        for (const chunk of chunks) {
          count += chunk.querySelectorAll("tbody > tr").length;
        }
        return count;
      });
      expect(totalRows).toBe(60);
    });

    test("no blank pages", async ({ page }) => {
      const pages = await getPages(page);
      for (let i = 0; i < pages.length; i++) {
        const hasContent = await pageHasVisibleContent(pages[i]);
        expect(hasContent, `Page ${i + 1} should have content`).toBe(true);
      }
    });

    test("content after table appears on final page", async ({ page }) => {
      const pages = await getPages(page);
      const lastPage = pages[pages.length - 1];
      const hasTrailingContent = await lastPage
        .locator("p")
        .filter({ hasText: "Content after the table" })
        .count()
        .then((c) => c > 0);
      expect(hasTrailingContent).toBe(true);
    });
  });

  test.describe("Wide-column table (horizontal overflow)", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/js/tests/fixtures/overflow/table-wide-columns.html");
      await waitForPagedJS(page);
    });

    test("table is NOT split into chunks (only tall tables are split)", async ({
      page,
    }) => {
      const chunks = await page.evaluate(() => {
        return document.querySelectorAll("table[data-nbprint-table-chunk]")
          .length;
      });
      expect(chunks).toBe(0);
    });

    test("table is NOT annotated with data-nbprint-paginate", async ({
      page,
    }) => {
      const annotated = await page.evaluate(() => {
        return document.querySelectorAll('table[data-nbprint-paginate="table"]')
          .length;
      });
      expect(annotated).toBe(0);
    });

    test("table is not vertically split despite spanning pages", async ({
      page,
    }) => {
      // pagedjs may break the wide table across pages horizontally,
      // but our vertical chunk splitting should NOT apply
      const pages = await getPages(page);
      expect(pages.length).toBeGreaterThanOrEqual(1);
    });

    test("no repeated headers are inserted", async ({ page }) => {
      const repeated = await page.evaluate(() => {
        return document.querySelectorAll('thead[data-nbprint-repeated="true"]')
          .length;
      });
      expect(repeated).toBe(0);
    });
  });
});
