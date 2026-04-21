/**
 * Post-pagination validation and repair.
 *
 * Runs AFTER pagedjs `previewer.preview()` returns but BEFORE
 * `nbprint.postprocess()` dispatches the `nbprint-done` event.
 * This is the safety net — it catches anything Phases 1-3 missed.
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

    // Remove pages explicitly marked as accidental blanks by Phase 3
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
 * previous phases. Uses scrollWidth/scrollHeight checks per the
 * roadmap. Returns an array of overflow descriptors.
 *
 * NOTE: This is purely diagnostic — it does NOT add data attributes.
 * Phase 3 already tags individual elements; Phase 4 just logs
 * anything that slipped through.
 */
function detectResidualOverflow() {
  const pages = document.querySelectorAll(".pagedjs_page");
  const overflows = [];

  for (let i = 0; i < pages.length; i++) {
    const page = pages[i];
    const contentArea = page.querySelector(".pagedjs_page_content");
    if (!contentArea) continue;

    // Report Phase 3 tagged elements
    const marked = contentArea.querySelectorAll("[data-nbprint-overflow]");
    for (const el of marked) {
      overflows.push({
        page: i + 1,
        element: describeElement(el),
        source: "phase3-marked",
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
        source: "phase4-scroll-overflow",
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

  console.debug(`[nbprint] postprocessing: validating ${pages.length} pages`);

  // 4.2: Remove blank pages
  const blankPagesRemoved = removeBlankPages();

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
