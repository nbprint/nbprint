export * from "./components/table-of-content";
import { createToc } from "./components/table-of-content";
import { Previewer, registerHandlers, Handler } from "pagedjs";
import "@fortawesome/fontawesome-free/js/all";

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

  // -------------------------------------------------------------------
  // 3.1  afterPageLayout — overflow detection
  // -------------------------------------------------------------------
  afterPageLayout(pageElement, page, breakToken, chunker) {
    const contentArea = pageElement.querySelector(".pagedjs_page_content");
    if (!contentArea) return;

    const pageBox = pageElement.getBoundingClientRect();

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

      // For images — shrink to fit
      const tag = el.tagName.toLowerCase();
      if (tag === "img" || tag === "svg" || tag === "canvas") {
        if (overflowsWidth) {
          el.style.maxWidth = pageBox.width + "px";
        }
        if (overflowsHeight) {
          el.style.maxHeight = pageBox.height + "px";
        }
        el.style.objectFit = "contain";
      } else {
        // Mark for post-processing
        el.setAttribute("data-nbprint-overflow", "true");
      }
    }

    // -------------------------------------------------------------------
    // 3.2  afterPageLayout — blank page detection
    // -------------------------------------------------------------------
    const hasVisibleContent = this._pageHasVisibleContent(contentArea);
    if (!hasVisibleContent) {
      pageElement.setAttribute("data-nbprint-blank", "true");
    }
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

  // -------------------------------------------------------------------
  // 3.4  renderNode — code block line-aware splitting
  // -------------------------------------------------------------------
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

  // -------------------------------------------------------------------
  // 3.5  onBreakToken — keep heading with next content
  // -------------------------------------------------------------------
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
