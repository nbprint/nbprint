/**
 * Post-pagination validation and repair.
 *
 * Runs AFTER pagedjs `previewer.preview()` returns but BEFORE
 * `nbprint.postprocess()` dispatches the `nbprint-done` event.
 * This is the safety net — it catches anything the earlier
 * preprocessing and handler hooks missed.
 */

/**
 * Remove accidental blank pages from the rendered output.
 * Pages marked data-nbprint-blank="intentional" are preserved.
 * Pages marked data-nbprint-blank="true" (accidental) are removed.
 * Returns the number of pages removed.
 */
function removeBlankPages() {
  const pages = document.querySelectorAll(".pagedjs_page");
  const removed = [];

  for (const page of pages) {
    const blankAttr = page.getAttribute("data-nbprint-blank");

    // Intentional blank pages are preserved
    if (blankAttr === "intentional") continue;

    // A page-box guarantees at least one page even when it is empty, so a page
    // it occupies is never an accidental blank.
    if (page.querySelector("[data-nbprint-page-box]")) continue;

    // Remove pages explicitly marked as accidental blanks by the
    // pagedjs afterPageLayout handler.
    if (blankAttr === "true") {
      removed.push(page);
    }
  }

  for (const page of removed) {
    page.remove();
  }

  if (removed.length > 0) {
    // Re-number remaining pages via CSS counter reset
    updatePageCounters();
    console.debug(
      `[nbprint] postprocessing: removed ${removed.length} blank page(s)`,
    );
  }

  return removed.length;
}

/**
 * Update pagedjs page counters after page removal.
 * Pagedjs uses CSS counters — we need to update the data attributes
 * that drive them so page numbers remain sequential.
 */
function updatePageCounters() {
  const pages = document.querySelectorAll(".pagedjs_page");
  let pageNum = 1;
  for (const page of pages) {
    page.setAttribute("data-page-number", pageNum);
    // Update the page counter content if present
    const counterEl = page.querySelector(".pagedjs_margin-bottom-center");
    if (counterEl) {
      const span = counterEl.querySelector(".pagedjs_margin-content");
      if (span) {
        span.textContent = String(pageNum);
      }
    }
    pageNum++;
  }
}

/**
 * Scan all pages for content areas that still overflow after all
 * earlier preprocessing and handler passes. Uses scrollWidth/scrollHeight
 * checks per the roadmap. Returns an array of overflow descriptors.
 *
 * NOTE: This is purely diagnostic — it does NOT add data attributes.
 * The afterPageLayout handler already tags individual elements; this
 * post-pagination pass just logs anything that slipped through.
 */
function detectResidualOverflow() {
  const pages = document.querySelectorAll(".pagedjs_page");
  const overflows = [];

  for (let i = 0; i < pages.length; i++) {
    const page = pages[i];
    const contentArea = page.querySelector(".pagedjs_page_content");
    if (!contentArea) continue;

    // Report elements tagged by the afterPageLayout handler
    const marked = contentArea.querySelectorAll("[data-nbprint-overflow]");
    for (const el of marked) {
      overflows.push({
        page: i + 1,
        element: describeElement(el),
        source: "handler-marked",
      });
    }

    // Check for scroll-based overflow on the content area itself
    const horizontalOverflow =
      contentArea.scrollWidth > contentArea.clientWidth + 2;
    const verticalOverflow =
      contentArea.scrollHeight > contentArea.clientHeight + 2;

    if (horizontalOverflow || verticalOverflow) {
      overflows.push({
        page: i + 1,
        element: "pagedjs_page_content",
        source: "postprocess-scroll-overflow",
        horizontalOverflow,
        verticalOverflow,
      });
    }
  }

  return overflows;
}

/**
 * Build a human-readable selector-like description of an element
 * for logging purposes.
 */
function describeElement(el) {
  let desc = el.tagName.toLowerCase();
  if (el.id) desc += `#${el.id}`;
  if (el.className && typeof el.className === "string") {
    desc += "." + el.className.trim().split(/\s+/).join(".");
  }
  return desc;
}

/**
 * Report page-boxes that produced fewer pages than they asked for.
 *
 * Padding a box up to its minimum would mean fabricating pagedjs page chrome, so this reports the
 * shortfall rather than inventing pages: a wrong page count is at least visible.
 *
 * @returns {Array<{id: string, want: number, got: number}>}
 */
function checkMinPages() {
  const shortfalls = [];
  for (const box of document.querySelectorAll("[data-nbprint-min-pages]")) {
    const want = parseInt(box.getAttribute("data-nbprint-min-pages"), 10);
    const id = box.getAttribute("data-nbprint-page-box");
    if (!Number.isFinite(want) || !id) continue;
    let got = 0;
    for (const page of document.querySelectorAll(".pagedjs_page")) {
      if (page.querySelector(`[data-nbprint-page-box="${id}"]`)) got += 1;
    }
    if (got < want) shortfalls.push({ id, want, got });
  }
  return shortfalls;
}

/**
 * Drop the leading-heading spacing on whichever heading starts a page.
 *
 * `--nbprint-heading-spacing` keeps a section heading clear of the cell above
 * it, but that space is wrong at the top of a page, where it indents the
 * heading below the page margin. CSS cannot express "first rendered thing on
 * the page": `:first-child` sees the zero-height and non-rendered siblings
 * Paged.js leaves behind, and the depth of the wrapper chain varies with the
 * document. Walking the laid-out pages is exact, and it runs after pagination
 * so it cannot perturb the layout it is measuring.
 *
 * @returns {number} how many headings were trimmed.
 */
function trimLeadingHeadingMargins() {
  const HEADINGS = new Set(["H1", "H2", "H3", "H4", "H5", "H6"]);
  let trimmed = 0;

  for (const page of document.querySelectorAll(".pagedjs_page")) {
    const area = page.querySelector(".pagedjs_page_content");
    if (!area) continue;

    // Descend through the wrapper chain to the first element that actually
    // occupies space, then take its leading heading, if it has one.
    let node = area;
    while (node) {
      const next = [...node.children].find((child) => {
        const box = child.getBoundingClientRect();
        return box.width > 0 && box.height > 0;
      });
      if (!next) break;
      if (HEADINGS.has(next.tagName)) {
        next.style.setProperty("margin-top", "0", "important");
        trimmed += 1;
        break;
      }
      node = next;
    }
  }

  return trimmed;
}

/**
 * Run post-pagination validation and repair.
 *
 * @param {object} configuration  The _nbprint_configuration object.
 * @returns {{ blankPagesRemoved: number, overflows: Array }}
 */
export function postvalidate(configuration) {
  if (configuration?.postprocessing === false)
    return { blankPagesRemoved: 0, overflows: [] };

  const pages = document.querySelectorAll(".pagedjs_page");
  if (pages.length === 0) return { blankPagesRemoved: 0, overflows: [] };

  const pageConfig = configuration?.page || {};

  console.debug(`[nbprint] postprocessing: validating ${pages.length} pages`);

  // 4.2: Remove blank pages (6.2: controlled by page.blank_page_removal)
  let blankPagesRemoved = 0;
  if (pageConfig.blank_page_removal !== false) {
    blankPagesRemoved = removeBlankPages();
  }

  for (const { id, want, got } of checkMinPages()) {
    console.warn(
      `[nbprint] postprocessing: page-box ${id} asked for ${want} page(s) but produced ${got}`,
    );
  }

  const headingsTrimmed = trimLeadingHeadingMargins();
  if (headingsTrimmed > 0) {
    console.debug(
      `[nbprint] postprocessing: trimmed leading margin on ${headingsTrimmed} page-leading heading(s)`,
    );
  }

  // 4.3: Detect residual overflow
  const overflows = detectResidualOverflow();
  if (overflows.length > 0) {
    console.warn(
      `[nbprint] postprocessing: ${overflows.length} element(s) still overflow after pagination:`,
    );
    for (const o of overflows) {
      console.warn(`  Page ${o.page}: ${o.element} (${o.source})`);
    }
  } else {
    console.debug("[nbprint] postprocessing: no overflow detected");
  }

  // Mark validation complete
  document
    .querySelector(".pagedjs_pages")
    ?.setAttribute("data-nbprint-validated", "true");

  return { blankPagesRemoved, overflows };
}
