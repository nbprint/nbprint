/**
 * Pre-pagination content measurement and scaling.
 *
 * Runs BEFORE pagedjs to proactively resize or annotate content that
 * won't fit within page dimensions.  This is complementary to the
 * defensive CSS — CSS constrains elements *inside* paginated pages,
 * but pagedjs measures the DOM *before* pagination, so elements
 * with explicit oversized dimensions cause bad chunking decisions.
 * This module fixes those dimensions up-front.
 */

/** Standard page sizes in CSS pixels (96 DPI). */
const PAGE_SIZES = {
  letter: { width: 816, height: 1056 }, // 8.5 × 11 in
  a4: { width: 794, height: 1123 }, // 210 × 297 mm
  a3: { width: 1123, height: 1587 }, // 297 × 420 mm
  legal: { width: 816, height: 1344 }, // 8.5 × 14 in
  tabloid: { width: 1056, height: 1632 }, // 11 × 17 in
};

/** Default page margin (0.5 in) in pixels. */
const DEFAULT_MARGIN_PX = 48;

/** Convert a CSS length string (e.g. "0.5in", "25.4mm") to pixels. */
function cssToPixels(value) {
  if (typeof value === "number") return value;
  const str = String(value).trim();
  const num = parseFloat(str);
  if (isNaN(num)) return 0;
  if (str.endsWith("in")) return num * 96;
  if (str.endsWith("cm")) return num * (96 / 2.54);
  if (str.endsWith("mm")) return num * (96 / 25.4);
  if (str.endsWith("pt")) return num * (96 / 72);
  if (str.endsWith("pc")) return num * (96 / 6);
  return num; // assume px
}

/**
 * Parse @page margins from document stylesheets.
 * Returns { top, right, bottom, left } in pixels.
 */
function getPageMargins() {
  let top = DEFAULT_MARGIN_PX;
  let right = DEFAULT_MARGIN_PX;
  let bottom = DEFAULT_MARGIN_PX;
  let left = DEFAULT_MARGIN_PX;

  for (const sheet of document.styleSheets) {
    let rules;
    try {
      rules = sheet.cssRules;
    } catch {
      continue; // cross-origin stylesheet
    }
    for (const rule of rules) {
      // CSSPageRule.type === 6
      if (rule.type !== 6) continue;

      const s = rule.style;
      const margin = s.getPropertyValue("margin");
      if (margin) {
        const parts = margin.trim().split(/\s+/);
        if (parts.length === 1) {
          top = right = bottom = left = cssToPixels(parts[0]);
        } else if (parts.length === 2) {
          top = bottom = cssToPixels(parts[0]);
          right = left = cssToPixels(parts[1]);
        } else if (parts.length === 3) {
          top = cssToPixels(parts[0]);
          right = left = cssToPixels(parts[1]);
          bottom = cssToPixels(parts[2]);
        } else {
          top = cssToPixels(parts[0]);
          right = cssToPixels(parts[1]);
          bottom = cssToPixels(parts[2]);
          left = cssToPixels(parts[3]);
        }
      }
      // Individual properties override shorthand
      const mt = s.getPropertyValue("margin-top");
      const mr = s.getPropertyValue("margin-right");
      const mb = s.getPropertyValue("margin-bottom");
      const ml = s.getPropertyValue("margin-left");
      if (mt) top = cssToPixels(mt);
      if (mr) right = cssToPixels(mr);
      if (mb) bottom = cssToPixels(mb);
      if (ml) left = cssToPixels(ml);
    }
  }

  return { top, right, bottom, left };
}

/**
 * Compute the usable content area for a single page.
 * Derives page size from configuration + @page CSS margins.
 */
export function getPageContentArea(configuration) {
  let pageWidth, pageHeight;

  const pageConfig = configuration?.page || {};
  const size = (pageConfig.size || "").toLowerCase().trim();

  if (size && PAGE_SIZES[size]) {
    ({ width: pageWidth, height: pageHeight } = PAGE_SIZES[size]);
  } else if (size) {
    // Custom size, e.g. "8.5in 11in"
    const parts = size.split(/[\sx]+/);
    if (parts.length === 2) {
      pageWidth = cssToPixels(parts[0]);
      pageHeight = cssToPixels(parts[1]);
    }
  }

  // Default to US Letter
  if (!pageWidth || !pageHeight) {
    ({ width: pageWidth, height: pageHeight } = PAGE_SIZES.letter);
  }

  if (pageConfig.orientation === "landscape") {
    [pageWidth, pageHeight] = [pageHeight, pageWidth];
  }

  const margins = getPageMargins();
  return {
    pageWidth,
    pageHeight,
    width: pageWidth - margins.left - margins.right,
    height: pageHeight - margins.top - margins.bottom,
  };
}

function scaleOversizedImages(contentRoot, contentArea) {
  for (const img of contentRoot.querySelectorAll("img")) {
    const attrW = parseFloat(img.getAttribute("width"));
    const attrH = parseFloat(img.getAttribute("height"));
    const w = img.naturalWidth || attrW || 0;
    const h = img.naturalHeight || attrH || 0;

    if (w > contentArea.width || h > contentArea.height) {
      img.style.maxWidth = contentArea.width + "px";
      img.style.maxHeight = contentArea.height + "px";
      img.style.objectFit = "contain";

      // Clear explicit attributes that would override CSS max-*
      if (attrW > contentArea.width) img.removeAttribute("width");
      if (attrH > contentArea.height) img.removeAttribute("height");
    }
  }
}

function scaleOversizedSVGs(contentRoot, contentArea) {
  for (const svg of contentRoot.querySelectorAll("svg")) {
    const attrW = parseFloat(svg.getAttribute("width")) || 0;
    const attrH = parseFloat(svg.getAttribute("height")) || 0;
    const box = svg.getBoundingClientRect();
    const w = attrW || box.width;
    const h = attrH || box.height;

    if (w <= contentArea.width && h <= contentArea.height) continue;

    // Ensure viewBox exists so the browser can scale properly
    if (!svg.getAttribute("viewBox") && w > 0 && h > 0) {
      svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    }

    const scale = Math.min(
      contentArea.width / Math.max(w, 1),
      contentArea.height / Math.max(h, 1),
    );
    svg.setAttribute("width", Math.floor(w * scale));
    svg.setAttribute("height", Math.floor(h * scale));
    svg.style.maxWidth = "100%";
  }
}

function scaleOversizedCharts(contentRoot, contentArea) {
  // Plotly charts
  for (const chart of contentRoot.querySelectorAll(".js-plotly-plot")) {
    const w = chart.offsetWidth || chart.getBoundingClientRect().width;
    if (w <= contentArea.width) continue;

    if (typeof window.Plotly?.relayout === "function") {
      try {
        window.Plotly.relayout(chart, { width: contentArea.width });
      } catch {
        chart.style.maxWidth = contentArea.width + "px";
        chart.style.overflow = "hidden";
      }
    } else {
      chart.style.maxWidth = contentArea.width + "px";
      chart.style.overflow = "hidden";
    }
  }

  // matplotlib containers — ensure they don't block image scaling
  for (const container of contentRoot.querySelectorAll(".jp-RenderedImage")) {
    container.style.maxWidth = "100%";
  }
}

function annotateTallTables(contentRoot, contentArea) {
  for (const table of contentRoot.querySelectorAll("table")) {
    const h = table.getBoundingClientRect().height || table.offsetHeight;
    if (h > contentArea.height) {
      table.setAttribute("data-nbprint-paginate", "table");
    }
  }
}

/**
 * 3.3: Split tall tables into page-sized chunks, each with its own thead.
 *
 * This runs BEFORE pagedjs so that pagedjs sees multiple small tables
 * instead of one giant table. No data is lost — every row appears in
 * exactly one chunk.
 *
 * GT tables: only repeat column heading rows, skip title/subtitle.
 */
function splitTallTables(contentRoot, contentArea, configuration) {
  if (configuration?.page?.table_header_repeat === false) return;

  const tables = contentRoot.querySelectorAll(
    'table[data-nbprint-paginate="table"]',
  );

  for (const table of tables) {
    const thead = table.querySelector("thead");
    const tbody = table.querySelector("tbody");
    if (!thead || !tbody) continue;

    const rows = Array.from(tbody.querySelectorAll(":scope > tr"));
    if (rows.length === 0) continue;

    const isGT = table.classList.contains("gt_table");

    // Build the header that will be repeated on each chunk.
    // For GT tables, skip title/subtitle rows.
    const repeatedHeader = isGT
      ? cloneGTColumnHeaders(thead)
      : thead.cloneNode(true);

    if (!repeatedHeader) continue;

    // Use a hidden measuring table to get accurate chunk heights.
    // Instead of summing individual row heights (which are inaccurate
    // due to border-collapse, table layout distribution, etc.) we add
    // rows one at a time and measure the real rendered table height.
    const measuringTable = document.createElement("table");
    for (const attr of table.attributes) {
      measuringTable.setAttribute(attr.name, attr.value);
    }
    measuringTable.style.visibility = "hidden";
    measuringTable.style.position = "absolute";
    measuringTable.style.width = table.getBoundingClientRect().width + "px";
    contentRoot.appendChild(measuringTable);

    // The first chunk shares a page with whatever content precedes the
    // table.  Estimate how far into the current logical page the table
    // starts so the first chunk is sized to fit the remaining space.
    // We must also account for any padding/margin the table's wrapper
    // elements add below the table itself.
    const contentTop = contentRoot.getBoundingClientRect().top;
    const tableTop = table.getBoundingClientRect().top;
    const offsetFromRoot = tableTop - contentTop;
    const offsetIntoPage = offsetFromRoot % contentArea.height;

    const firstChunkMaxHeight = contentArea.height - offsetIntoPage;

    const maxHeight = contentArea.height;
    const chunks = [];
    let currentChunk = [];
    let isFirstChunk = true;

    // Reset the measuring table with the appropriate header for the
    // current chunk (first chunk uses full thead, continuations use
    // column-only header for GT tables).
    function resetMeasuringTable() {
      measuringTable.innerHTML = "";
      const header = isFirstChunk
        ? thead.cloneNode(true)
        : repeatedHeader.cloneNode(true);
      measuringTable.appendChild(header);
      const newTbody = document.createElement("tbody");
      newTbody.className = tbody.className;
      measuringTable.appendChild(newTbody);
      return newTbody;
    }

    let measuringTbody = resetMeasuringTable();

    for (const row of rows) {
      const clonedRow = row.cloneNode(true);
      measuringTbody.appendChild(clonedRow);

      const tableHeight = measuringTable.getBoundingClientRect().height;
      const limit = isFirstChunk ? firstChunkMaxHeight : maxHeight;

      if (tableHeight > limit && currentChunk.length > 0) {
        // This row pushed us over — remove it, finalize the current
        // chunk, then start a new chunk beginning with this row.
        clonedRow.remove();
        chunks.push(currentChunk);
        currentChunk = [];
        isFirstChunk = false;
        measuringTbody = resetMeasuringTable();
        measuringTbody.appendChild(row.cloneNode(true));
      }

      currentChunk.push(row);
    }
    if (currentChunk.length > 0) {
      chunks.push(currentChunk);
    }

    measuringTable.remove();

    // If it fits in one chunk, no splitting needed
    if (chunks.length <= 1) continue;

    // Build replacement tables
    const fragment = document.createDocumentFragment();

    for (let i = 0; i < chunks.length; i++) {
      const chunkTable = document.createElement("table");

      // Copy attributes from original (class, style, data-* etc)
      for (const attr of table.attributes) {
        chunkTable.setAttribute(attr.name, attr.value);
      }
      // Remove the paginate annotation — chunks should fit
      chunkTable.removeAttribute("data-nbprint-paginate");
      chunkTable.setAttribute(
        "data-nbprint-table-chunk",
        `${i + 1}/${chunks.length}`,
      );

      // First chunk gets the original full thead (with title/subtitle for GT)
      // Continuation chunks get column-only headers
      if (i === 0) {
        chunkTable.appendChild(thead.cloneNode(true));
      } else {
        const header = repeatedHeader.cloneNode(true);
        header.setAttribute("data-nbprint-repeated", "true");
        chunkTable.appendChild(header);
      }

      const chunkBody = document.createElement("tbody");
      chunkBody.className = tbody.className;
      for (const row of chunks[i]) {
        chunkBody.appendChild(row.cloneNode(true));
      }
      chunkTable.appendChild(chunkBody);

      // Copy tfoot if present (only on last chunk)
      if (i === chunks.length - 1) {
        const tfoot = table.querySelector("tfoot");
        if (tfoot) {
          chunkTable.appendChild(tfoot.cloneNode(true));
        }
      }

      fragment.appendChild(chunkTable);
    }

    // Replace the original table with the chunks
    const parent = table.parentNode;
    parent.replaceChild(fragment, table);

    // If the parent container has break-inside: avoid (applied by
    // .pagedjs_page .jp-OutputArea-output in CSS), pagedjs would treat
    // all chunks as a single atomic block.  Set an inline override so
    // the chunks can flow naturally across page breaks.
    const outputDiv = parent.closest(".jp-OutputArea-output") || parent;
    outputDiv.style.breakInside = "auto";
    // .jp-OutputArea-child has `break-inside: avoid-page` from
    // notebook.css; override it too so the chunks can split across
    // pages.
    const childDiv = outputDiv.closest(".jp-OutputArea-child");
    if (childDiv) childDiv.style.breakInside = "auto";

    console.debug(
      `[nbprint] preprocessing: split table into ${chunks.length} chunks`,
    );
  }
}

/**
 * Clone GT-aware headers: only the column heading rows,
 * skipping title/subtitle rows.
 */
function cloneGTColumnHeaders(sourceThead) {
  const thead = document.createElement("thead");
  thead.className = sourceThead.className;

  for (const row of sourceThead.children) {
    // Skip title/subtitle rows
    if (row.classList.contains("gt_heading")) {
      const hasTitle = row.querySelector(".gt_title, .gt_subtitle");
      if (hasTitle) continue;
    }

    thead.appendChild(row.cloneNode(true));
  }

  return thead.children.length > 0 ? thead : null;
}

/**
 * Override break-inside: avoid for non-table content taller than a single page.
 * Tables are already handled by splitTallTables; this covers code blocks and
 * other tall output wrappers that would otherwise be pushed to the next page.
 *
 * For tall code blocks (<pre>), we also wrap individual lines in block-level
 * spans so pagedjs has breakpoints between lines (plain text nodes don't
 * provide breakpoints).
 */
function allowTallContentToBreak(contentRoot, contentArea) {
  for (const el of contentRoot.querySelectorAll(".jp-OutputArea-output")) {
    // Skip elements already handled by splitTallTables
    if (el.querySelector("[data-nbprint-table-chunk]")) continue;
    if (el.getBoundingClientRect().height > contentArea.height) {
      el.style.breakInside = "auto";

      // Wrap code lines so pagedjs can break between them
      for (const pre of el.querySelectorAll("pre")) {
        wrapCodeLinesForBreaking(pre);
      }
    }
  }
}

/**
 * Wrap individual lines in a <pre> element with block-level spans
 * that prevent mid-line breaks while allowing breaks between lines.
 * This must run before pagedjs so it has breakpoints to work with.
 */
function wrapCodeLinesForBreaking(preElement) {
  const codeEl = preElement.querySelector("code") || preElement;
  if (codeEl.getAttribute("data-nbprint-lines") === "true") return;

  const text = codeEl.textContent;
  if (!text || !text.includes("\n")) return;

  const lines = text.split("\n");
  if (lines.length <= 1) return;

  const fragment = document.createDocumentFragment();
  for (const line of lines) {
    const span = document.createElement("span");
    span.style.display = "block";
    span.style.breakInside = "avoid";
    span.textContent = line;
    fragment.appendChild(span);
  }

  codeEl.textContent = "";
  codeEl.appendChild(fragment);
  codeEl.setAttribute("data-nbprint-lines", "true");
}

/**
 * Tag content cells whose only visible content is a heading so that CSS
 * can apply `break-after: avoid` to the whole cell wrapper. pagedjs
 * honours break-after:avoid by pulling the heading to the next page
 * when the following block cannot fit on the current page.
 *
 * We previously tried to physically merge the heading into the next
 * cell. That backfired on notebooks where the next cell's total
 * content already exceeded one page: pagedjs would then be forced to
 * break INSIDE the merged cell, often stranding the heading. Tagging
 * is enough, as long as we don't over-constrain with break-inside:avoid
 * on the target side.
 */
function tagHeadingOnlyCells(contentRoot) {
  const HEADING = /^H[1-6]$/;
  const cells = contentRoot.querySelectorAll(
    '[class*="nbprint-config-content-"]',
  );
  for (const cell of cells) {
    let lastVisible = null;
    for (const el of cell.querySelectorAll("*")) {
      if (el.children.length > 0) continue;
      const text = (el.textContent || "").trim();
      if (!text) continue;
      lastVisible = el;
    }
    if (!lastVisible) continue;
    let h = lastVisible;
    while (h && h !== cell && !HEADING.test(h.tagName)) h = h.parentElement;
    if (!h || !HEADING.test(h.tagName)) continue;
    const cellText = (cell.textContent || "").trim();
    const headingText = (h.textContent || "").trim();
    if (cellText.length > headingText.length + 10) continue;
    cell.setAttribute("data-nbprint-heading-only", "true");
  }
}

/**
 * Ensure every numbered section heading ("1 · Title", "2 · Title", ...)
 * starts on a new page. If the heading cell is not already preceded by
 * a `.pagebreak` sibling (or equivalent), insert one. This lets authors
 * drop most of their manual `newpage()` calls and get consistent
 * section starts for free.
 *
 * We match section headings by the "N · " prefix generated by the
 * standard nbprint section template. The check is deliberately narrow
 * so subsection headings within a section are not forced onto new
 * pages.
 */
function forcePageBreakBeforeSections(contentRoot) {
  const SECTION_RE = /^\s*\d+\s*·/;
  for (const h of contentRoot.querySelectorAll("h1, h2")) {
    const text = (h.textContent || "").trim();
    if (!SECTION_RE.test(text)) continue;
    // Find the enclosing cell wrapper — that's the element pagedjs
    // paginates around.
    let cell = h;
    while (
      cell &&
      cell !== contentRoot &&
      !(cell.className || "").includes("nbprint-config-content-")
    ) {
      cell = cell.parentElement;
    }
    if (!cell || cell === contentRoot) continue;
    // Already preceded by a pagebreak element? Do nothing.
    const prev = cell.previousElementSibling;
    if (prev && prev.classList && prev.classList.contains("pagebreak"))
      continue;
    // Insert a fresh pagebreak element immediately before the cell.
    const pb = document.createElement("p");
    pb.className = "pagebreak";
    pb.setAttribute("data-nbprint-auto-pagebreak", "true");
    cell.parentNode.insertBefore(pb, cell);
  }
}

/**
 * Shrink cells that overflow the page by a small amount so they fit on
 * a single page. This handles the common case where two plots of ~50%
 * page height add up to just over a page (by a few percent) — without
 * this pass pagedjs breaks between them, wasting half the next page.
 *
 * The scale is applied as a CSS `zoom` on each image/SVG/plotly element
 * inside the cell so text (captions, axis labels) scales proportionally
 * with the figure. We cap the scale-down at `MAX_SHRINK` (25%) to avoid
 * producing illegibly small content; cells that need more than that
 * are left alone for pagedjs to split naturally.
 */
function fitCellsToPage(contentRoot, contentArea) {
  const pageH = contentArea.height;
  const pageW = contentArea.width;
  const cells = contentRoot.querySelectorAll(
    '[class*="nbprint-config-content-"]',
  );
  for (const cell of cells) {
    const rect = cell.getBoundingClientRect();
    const measuredH = rect.height;
    const measuredW = rect.width || pageW;
    // Correct for the fact that pre-pagination measurements use the
    // full viewport width, which is wider than the actual page content
    // area. Wrapped text and tables render shorter at narrower width.
    const widthRatio = Math.min(1, pageW / measuredW);
    const estH = measuredH * Math.sqrt(widthRatio);
    if (estH <= pageH) continue;
    // Figures-only cells can be shrunk more aggressively than mixed or
    // text-heavy ones. If a cell contains tables or non-trivial text
    // blocks we keep the cap at 25%; for pure-figure cells (multiple
    // plots, heatmaps, etc.) we allow down to 50% so cells with 3+
    // charts can still fit on one page.
    const hasFigs =
      cell.querySelectorAll(
        "img, svg, .js-plotly-plot, .jp-RenderedImage, canvas",
      ).length > 0;
    const hasTablesOrText = cell.querySelector("table, pre") !== null;
    const maxShrink = hasFigs && !hasTablesOrText ? 0.5 : 0.25;
    const scale = pageH / estH;
    if (scale < 1 - maxShrink) continue; // too much shrink, skip
    if (shrinkCellFigures(cell, scale)) {
      cell.setAttribute("data-nbprint-fit-scale", scale.toFixed(3));
    }
  }
}

/**
 * Apply a uniform zoom scale to figure-like elements inside a cell, or
 * to the cell itself as a fallback if there are no figures. Using CSS
 * zoom (rather than transform: scale) keeps the element in document
 * flow so pagedjs measures the shrunken height.
 */
function shrinkCellFigures(cell, scale) {
  const figs = cell.querySelectorAll(
    "img, svg, .js-plotly-plot, .jp-RenderedImage, canvas",
  );
  if (figs.length === 0) return false;
  for (const f of figs) {
    const prev = f.style.zoom ? parseFloat(f.style.zoom) : 1;
    f.style.zoom = String(prev * scale);
  }
  return true;
}

/**
 * For each heading-only cell, check whether it would fit on a single
 * page alongside the cell that follows it. If the next cell is just
 * slightly too tall, shrink its figures so heading + content ride on
 * the same page instead of the heading orphaning.
 *
 * This is the companion to `forcePageBreakBeforeSections`: the page
 * break puts the heading at the top of a fresh page, but if the
 * following cell is itself close to one page in height, the heading
 * would be stranded alone. We reserve a small budget for the heading
 * (HEAD_BUDGET) and shrink the next cell enough that both fit.
 */
function shrinkCellAfterHeading(contentRoot, contentArea) {
  const pageH = contentArea.height;
  const pageW = contentArea.width;
  const HEAD_BUDGET = 100; // heading height + margin
  const MIN_SCALE = 0.75;
  const budget = pageH - HEAD_BUDGET;
  const headingCells = contentRoot.querySelectorAll(
    '[data-nbprint-heading-only="true"]',
  );
  for (const cell of headingCells) {
    // Find the next cell wrapper in document order that is not itself
    // heading-only.
    let next = null;
    const walker = document.createTreeWalker(
      contentRoot,
      NodeFilter.SHOW_ELEMENT,
      {
        acceptNode: (n) =>
          (n.className || "").includes("nbprint-config-content-") &&
          n.getAttribute("data-nbprint-heading-only") !== "true"
            ? NodeFilter.FILTER_ACCEPT
            : NodeFilter.FILTER_SKIP,
      },
    );
    walker.currentNode = cell;
    next = walker.nextNode();
    while (next && cell.contains(next)) next = walker.nextNode();
    if (!next) continue;

    // Wrap the heading element together with the next cell's first
    // output in an atomic `break-inside: avoid` container so pagedjs
    // cannot orphan the heading. We wrap OUTSIDE the
    // `.jp-OutputArea-output` div so the heading doesn't inherit
    // stderr/warning backgrounds or any zoom applied to the output.
    const headingEl = cell.querySelector("h1, h2, h3, h4, h5, h6");
    const firstChild = next.querySelector(".jp-OutputArea-child");
    if (headingEl && firstChild) {
      const pair = document.createElement("div");
      pair.className = "nbprint-heading-pair";
      pair.setAttribute("data-nbprint-heading-pair", "true");
      pair.style.breakInside = "avoid";
      firstChild.parentNode.insertBefore(pair, firstChild);
      pair.appendChild(headingEl);
      pair.appendChild(firstChild);
      // Neutralise the now-empty heading cell so it adds no height.
      cell.style.display = "none";
      cell.setAttribute("data-nbprint-heading-moved", "true");
    }

    // Pre-pagination measurements use the full viewport width, which is
    // wider than the actual page content area. Tables and word-wrapped
    // text render shorter at narrower width, so we estimate the actual
    // post-pagedjs height using the width ratio.
    const rect = next.getBoundingClientRect();
    const measuredH = rect.height;
    const measuredW = rect.width || pageW;
    const widthRatio = Math.min(1, pageW / measuredW);
    const estH = measuredH * Math.sqrt(widthRatio);
    if (estH <= budget) continue;
    let scale = budget / estH;
    if (scale > 1) continue;
    if (scale < MIN_SCALE) scale = MIN_SCALE;
    if (shrinkCellFigures(next, scale)) {
      next.setAttribute("data-nbprint-fit-scale", scale.toFixed(3));
    }
  }
}

/**
 * Split multi-output cells across pages by inserting explicit page
 * breaks between `.jp-OutputArea-child` siblings whose cumulative
 * height would exceed the page budget. This works around a pagedjs
 * quirk where a cell with several medium-height outputs (each
 * individually `break-inside: avoid-page`) can overflow the page
 * because pagedjs fails to split between siblings.
 *
 * We run this AFTER the heading-pair and fit-to-page passes so we see
 * the final sibling set (including the injected heading pair) and final
 * figure sizes.
 */
function splitMultiOutputCells(contentRoot, contentArea) {
  const pageH = contentArea.height;
  const areas = contentRoot.querySelectorAll(".jp-OutputArea");
  for (const area of areas) {
    const kids = Array.from(area.children).filter(
      (c) =>
        c.classList.contains("jp-OutputArea-child") ||
        c.classList.contains("nbprint-heading-pair"),
    );
    if (kids.length < 2) continue;
    let cumH = 0;
    for (const kid of kids) {
      const h = kid.getBoundingClientRect().height;
      if (cumH > 0 && cumH + h > pageH) {
        // If the kid itself is taller than a full page there is no
        // benefit to inserting a pagebreak before it — the kid will
        // overflow whichever page it lands on and pagedjs needs to
        // split it internally. Starting it on the current page uses
        // the remaining space rather than wasting it.
        if (h > pageH) {
          // Let the kid flow on current page; allow it to split by
          // unlocking its break-inside.
          kid.style.breakInside = "auto";
          cumH += h;
          continue;
        }
        const pb = document.createElement("p");
        pb.className = "pagebreak";
        pb.setAttribute("data-nbprint-auto-break", "true");
        pb.style.margin = "0";
        pb.style.padding = "0";
        pb.style.height = "0";
        area.insertBefore(pb, kid);
        cumH = h;
      } else {
        cumH += h;
      }
    }
  }
}

/**
 * Run all pre-pagination preprocessing on the content root.
 *
 * @param {Element} contentRoot  The <main> element containing report content.
 * @param {object}  configuration  The _nbprint_configuration object.
 */
export function preprocess(contentRoot, configuration) {
  if (!contentRoot) return;
  if (configuration?.preprocessing === false) return;

  const contentArea = getPageContentArea(configuration);
  console.debug(
    `[nbprint] preprocessing: page content area ${contentArea.width}\u00d7${contentArea.height}px`,
  );

  scaleOversizedImages(contentRoot, contentArea);
  scaleOversizedSVGs(contentRoot, contentArea);
  scaleOversizedCharts(contentRoot, contentArea);
  annotateTallTables(contentRoot, contentArea);
  splitTallTables(contentRoot, contentArea, configuration);
  allowTallContentToBreak(contentRoot, contentArea);
  fitCellsToPage(contentRoot, contentArea);
  tagHeadingOnlyCells(contentRoot);
  forcePageBreakBeforeSections(contentRoot);
  shrinkCellAfterHeading(contentRoot, contentArea);
  splitMultiOutputCells(contentRoot, contentArea);

  contentRoot.setAttribute("data-nbprint-preprocessed", "true");
}
