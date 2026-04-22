export * from "./components/table-of-content";
import { createToc } from "./components/table-of-content";
import { Previewer, registerHandlers, Handler } from "pagedjs";
import "@fortawesome/fontawesome-free/js/all";

/**
 * Module-level configuration reference.
 * Set by `build()` before pagedjs runs so that the handler class
 * can read page-level settings (overflow_strategy, etc.).
 */
let _pageConfig = {};

/**
 * Sanitize element IDs so they are valid CSS selectors.
 * Jupyter converts markdown headings like "Summary & Performance"
 * into IDs containing characters (& · etc.) that break querySelector.
 * We rewrite those IDs before pagedjs runs and update any anchors
 * that reference them.
 */
function sanitizeIds(content) {
  const idMap = new Map();
  content.querySelectorAll("[id]").forEach((el) => {
    const oldId = el.id;
    // Replace any character that is not alphanumeric, hyphen, or underscore
    const newId = oldId
      .replace(/[^a-zA-Z0-9_-]/g, "-")
      .replace(/-{2,}/g, "-")
      .replace(/^-|-$/g, "");
    if (newId !== oldId && newId.length > 0) {
      el.id = newId;
      idMap.set(oldId, newId);
    }
  });
  if (idMap.size > 0) {
    content.querySelectorAll("a[href^='#']").forEach((a) => {
      const target = decodeURIComponent(a.getAttribute("href").slice(1));
      if (idMap.has(target)) {
        a.setAttribute("href", "#" + idMap.get(target));
      }
    });
  }
}

/**
 * Check if a heading tag name (e.g. "H2") matches.
 */
function isHeadingTag(tagName) {
  return /^H[1-6]$/i.test(tagName);
}

export class handlers extends Handler {
  constructor(chunker, polisher, caller) {
    super(chunker, polisher, caller);
  }

  beforeParsed(content) {
    sanitizeIds(content);
    createToc({
      content,
      tocElement: "#toc",
      titleElements: ["h1", "h2", "h3", "h4"],
    });
  }

  afterPageLayout(pageElement, page, breakToken, chunker) {
    const contentArea = pageElement.querySelector(".pagedjs_page_content");
    if (!contentArea) return;

    const pageBox = pageElement.getBoundingClientRect();
    const strategy = _pageConfig.overflow_strategy || "scale";

    // Walk all elements inside the page content area
    const walker = document.createTreeWalker(
      contentArea,
      NodeFilter.SHOW_ELEMENT,
    );
    let node;
    while ((node = walker.nextNode())) {
      // Skip container elements — only check leaf-level content
      if (node.children && node.children.length > 0) continue;

      const el = node;
      const rect = el.getBoundingClientRect();

      // Skip invisible elements
      if (rect.width === 0 && rect.height === 0) continue;

      const overflowsWidth = rect.right > pageBox.right + 1;
      const overflowsHeight = rect.bottom > pageBox.bottom + 1;

      if (!overflowsWidth && !overflowsHeight) continue;

      // 6.4: Per-element override via data-nbprint-overflow attribute
      // If the element (or an ancestor) has a specific strategy, use that
      const elStrategy =
        el
          .closest("[data-nbprint-overflow]")
          ?.getAttribute("data-nbprint-overflow") || strategy;

      // Skip elements already marked as overflow from a previous pass
      if (elStrategy === "true") continue;

      this._applyOverflowStrategy(el, elStrategy, pageBox, {
        overflowsWidth,
        overflowsHeight,
      });
    }

    const hasVisibleContent = this._pageHasVisibleContent(contentArea);
    if (!hasVisibleContent) {
      // Only mark as blank if the page wasn't created by an explicit
      // CSS break rule (break-before/break-after: page|recto|verso|left|right).
      // Intentional blank pages should be preserved.
      const intentional = this._isIntentionalBlank(pageElement, breakToken);
      if (intentional) {
        pageElement.setAttribute("data-nbprint-blank", "intentional");
      } else {
        pageElement.setAttribute("data-nbprint-blank", "true");
      }
    }
  }

  /**
   * Apply the chosen overflow strategy to an element.
   *
   * Strategies (6.1):
   *   "scale" — shrink images/SVGs to fit; mark others (default)
   *   "clip"  — hide overflow via CSS, no resize
   *   "warn"  — log only, no DOM changes
   *   "break" — force a page break before the element
   */
  _applyOverflowStrategy(
    el,
    strategy,
    pageBox,
    { overflowsWidth, overflowsHeight },
  ) {
    const tag = el.tagName.toLowerCase();

    switch (strategy) {
      case "scale":
        if (tag === "img" || tag === "svg" || tag === "canvas") {
          if (overflowsWidth) el.style.maxWidth = pageBox.width + "px";
          if (overflowsHeight) el.style.maxHeight = pageBox.height + "px";
          el.style.objectFit = "contain";
        } else {
          el.setAttribute("data-nbprint-overflow", "true");
        }
        break;

      case "clip":
        el.style.overflow = "hidden";
        if (overflowsWidth) el.style.maxWidth = pageBox.width + "px";
        if (overflowsHeight) el.style.maxHeight = pageBox.height + "px";
        el.setAttribute("data-nbprint-overflow", "clip");
        break;

      case "warn":
        console.warn(
          `[nbprint] overflow (warn-only): <${tag}> overflows page`,
          el,
        );
        el.setAttribute("data-nbprint-overflow", "warn");
        break;

      case "break":
        el.style.breakBefore = "page";
        el.setAttribute("data-nbprint-overflow", "break");
        break;

      default:
        // Unknown strategy — fall through to scale behavior
        el.setAttribute("data-nbprint-overflow", "true");
        break;
    }
  }

  /**
   * Determine if a blank page was intentionally created via CSS break rules.
   *
   * A blank page is intentional when:
   * - The break token's node (next content) has break-before: page|recto|verso|left|right
   * - The previous page's last element has break-after: page|recto|verso|left|right
   * - The page itself carries a pagedjs class indicating a forced break
   */
  _isIntentionalBlank(pageElement, breakToken) {
    const BREAK_VALUES = new Set([
      "page",
      "left",
      "right",
      "recto",
      "verso",
      "always",
    ]);

    // Check if break token's node has an explicit break-before
    if (breakToken?.node) {
      const node =
        breakToken.node.nodeType === Node.ELEMENT_NODE
          ? breakToken.node
          : breakToken.node.parentElement;
      if (node) {
        const style = getComputedStyle(node);
        if (BREAK_VALUES.has(style.breakBefore)) return true;
        // Legacy property
        if (BREAK_VALUES.has(style.pageBreakBefore)) return true;
      }
    }

    // Check if the previous page's last content element has break-after
    const prevPage = pageElement.previousElementSibling;
    if (prevPage?.classList?.contains("pagedjs_page")) {
      const prevContent = prevPage.querySelector(".pagedjs_page_content");
      if (prevContent) {
        // Find the last non-empty element in the previous page
        const allEls = prevContent.querySelectorAll("*");
        for (let i = allEls.length - 1; i >= 0; i--) {
          const el = allEls[i];
          if (el.tagName?.toLowerCase() === "br") continue;
          const style = getComputedStyle(el);
          if (BREAK_VALUES.has(style.breakAfter)) return true;
          if (BREAK_VALUES.has(style.pageBreakAfter)) return true;
          break;
        }
      }
    }

    return false;
  }

  /**
   * Check if a content area has any visible children.
   */
  _pageHasVisibleContent(contentArea) {
    const children = contentArea.querySelectorAll("*");
    for (const child of children) {
      // Skip elements that are purely structural
      const rect = child.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0) {
        // Check for actual text or media content
        const tag = child.tagName.toLowerCase();
        if (
          tag === "img" ||
          tag === "svg" ||
          tag === "canvas" ||
          tag === "video" ||
          tag === "table"
        ) {
          return true;
        }
        if (child.textContent && child.textContent.trim().length > 0) {
          return true;
        }
      }
    }
    return false;
  }

  renderNode(clone, sourceNode) {
    if (!sourceNode || !clone) return;
    const tag = sourceNode.tagName?.toLowerCase();

    // Only handle <pre> elements (code blocks)
    if (tag !== "pre") return;

    // Add a class so CSS can target code block fragments
    clone.classList.add("nbprint-code-fragment");
    // Ensure the code block allows breaks between lines but not mid-line
    // by wrapping each line in a span with break-inside: avoid
    this._wrapCodeLines(clone);
  }

  /**
   * Wrap individual lines in a <pre> block with spans that prevent
   * mid-line breaks while allowing breaks between lines.
   */
  _wrapCodeLines(preElement) {
    // Only process if the pre contains raw text or a single code child
    const codeEl = preElement.querySelector("code") || preElement;

    // Skip if already processed
    if (codeEl.getAttribute("data-nbprint-lines") === "true") return;

    const text = codeEl.textContent;
    if (!text || !text.includes("\n")) return;

    const lines = text.split("\n");
    // Only process if there are multiple lines
    if (lines.length <= 1) return;

    // Build new content with line-wrapping spans
    const fragment = document.createDocumentFragment();
    for (let i = 0; i < lines.length; i++) {
      const span = document.createElement("span");
      span.style.display = "block";
      span.style.breakInside = "avoid";
      span.textContent = lines[i];
      fragment.appendChild(span);
    }

    codeEl.textContent = "";
    codeEl.appendChild(fragment);
    codeEl.setAttribute("data-nbprint-lines", "true");
  }

  onBreakToken(breakToken, overflow, rendered) {
    if (!breakToken || !breakToken.node) return;

    const node = breakToken.node;

    // Walk up to find the actual element (breakToken.node may be a text node)
    const element =
      node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
    if (!element) return;

    // Check if the break is happening right after a heading
    // Look at the preceding sibling in the source content
    let prev = element.previousElementSibling;

    // Skip empty/whitespace-only elements
    while (
      prev &&
      prev.textContent.trim().length === 0 &&
      !prev.querySelector("img, svg, canvas, table")
    ) {
      prev = prev.previousElementSibling;
    }

    if (!prev) return;

    // If the previous element is a heading, move the break point
    // before the heading so it goes to the next page with its content
    if (isHeadingTag(prev.tagName)) {
      // Set the break token to the heading node so it moves to next page
      breakToken.node = prev;
      breakToken.offset = 0;
    }
  }
}

export const build = async (configuration) => {
  // Store page config for handler access
  _pageConfig = configuration.page || {};

  // Attach CSS Selector to body so it can be used in downstream CSS
  // Do this before any pagedjs processing so that elements can adjust
  // their styles before chunking or previewing
  document.body.classList.add("pagedjs");

  // Attach orientation class to body
  if (configuration.page.orientation) {
    document.body.setAttribute(
      `data-pagedjs-orientation`,
      configuration.page.orientation,
    );
  }

  if (configuration.page.size) {
    document.body.setAttribute(`data-pagedjs-size`, configuration.page.size);
  }

  const config = {
    auto: true,
    before: undefined,
    after: undefined,
    content: undefined,
    stylesheets: undefined,
    renderTo: undefined,
    settings: undefined,
  };

  const previewer = new Previewer(config);
  registerHandlers(handlers);

  if (config.before) {
    await config.before();
  }

  if (config.auto !== false) {
    const done = await previewer.preview(
      config.content,
      config.stylesheets,
      config.renderTo,
    );
  }

  if (config.after) {
    await config.after(done);
  }
};
