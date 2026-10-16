import { test, expect } from "@playwright/test";

async function waitForPagedJS(page, timeout = 30000) {
  await page.waitForSelector(".pagedjs_pages", { timeout });
  await page.waitForTimeout(500);
}

// paged.js leaves a call marker carrying the note's class in the text, so the
// notes themselves are the class members without data-footnote-call.
const NOTES = ".nbprint-footnote:not([data-footnote-call])";

test.describe("Footnotes", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/js/tests/fixtures/footnotes/paged.html");
    await waitForPagedJS(page);
  });

  test("the document paginates onto more than one page", async ({ page }) => {
    expect(await page.locator(".pagedjs_page").count()).toBeGreaterThan(1);
  });

  test("every note moves into a footnote area", async ({ page }) => {
    const notes = await page.locator(NOTES).count();
    const placed = await page
      .locator(`.pagedjs_footnote_area ${NOTES}`)
      .count();
    expect(notes).toBe(3);
    expect(placed).toBe(notes);
  });

  test("each note sits on the same page as its call", async ({ page }) => {
    const pairs = await page.evaluate(() =>
      [...document.querySelectorAll("[data-footnote-call]")].map((call) => {
        const note = document.querySelector(
          `[data-footnote-marker][data-ref="${call.dataset.ref}"]`,
        );
        return {
          callPage: call.closest(".pagedjs_page")?.dataset.pageNumber,
          notePage: note?.closest(".pagedjs_page")?.dataset.pageNumber,
        };
      }),
    );
    expect(pairs).toHaveLength(3);
    for (const { callPage, notePage } of pairs) {
      expect(notePage).toBeDefined();
      expect(notePage).toBe(callPage);
    }
    // The fixture cites two notes on the first page and one later on
    expect(pairs[0].callPage).toBe("1");
    expect(pairs[2].callPage).not.toBe("1");
  });

  test("the separator rule is drawn only above pages with notes", async ({
    page,
  }) => {
    const borders = await page.evaluate(() =>
      [...document.querySelectorAll(".pagedjs_footnote_content")].map((el) => ({
        empty: el.classList.contains("pagedjs_footnote_empty"),
        border: getComputedStyle(el).borderTopStyle,
      })),
    );
    expect(borders.some((b) => !b.empty)).toBe(true);
    for (const { empty, border } of borders) {
      expect(border).toBe(empty ? "none" : "solid");
    }
  });

  test("calls are superscript whatever the font", async ({ page }) => {
    const call = await page.evaluate(() => {
      const el = document.querySelector("[data-footnote-call]");
      const style = getComputedStyle(el, "::after");
      return {
        verticalAlign: style.verticalAlign,
        fontSize: parseFloat(style.fontSize),
        textSize: parseFloat(getComputedStyle(el.parentElement).fontSize),
      };
    });
    expect(call.verticalAlign).toBe("super");
    expect(call.fontSize).toBeLessThan(call.textSize);
  });

  test("notes use the report's content font", async ({ page }) => {
    const fonts = await page.evaluate(() => ({
      body: getComputedStyle(document.querySelector("#first")).fontFamily,
      note: getComputedStyle(document.querySelector(".pagedjs_footnote_area"))
        .fontFamily,
    }));
    expect(fonts.note).toBe(fonts.body);
  });
});

test.describe("Footnotes without paged.js", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/js/tests/fixtures/footnotes/unpaged.html");
    await page.waitForSelector('html[data-nbprint-paged="done"]', {
      state: "attached",
    });
  });

  test("the note stays in the text as a parenthetical", async ({ page }) => {
    const note = await page.evaluate(() => {
      const el = document.querySelector(".nbprint-footnote");
      return {
        inParagraph: el.parentElement.id === "first",
        before: getComputedStyle(el, "::before").content,
        after: getComputedStyle(el, "::after").content,
      };
    });
    expect(note).toEqual({ inParagraph: true, before: '" ("', after: '")"' });
  });
});
