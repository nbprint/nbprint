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

  contentRoot.setAttribute("data-nbprint-preprocessed", "true");
}
