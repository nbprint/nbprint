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

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Page dimension computation
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// 2.2  Scale oversized images
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// 2.2  Scale oversized SVGs
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// 2.3  Scale oversized charts (Plotly, matplotlib)
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// 2.4  Annotate tall tables for chunking
// ---------------------------------------------------------------------------

function annotateTallTables(contentRoot, contentArea) {
  for (const table of contentRoot.querySelectorAll("table")) {
    const h = table.getBoundingClientRect().height || table.offsetHeight;
    if (h > contentArea.height) {
      table.setAttribute("data-nbprint-paginate", "table");
    }
  }
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

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

  contentRoot.setAttribute("data-nbprint-preprocessed", "true");
}
