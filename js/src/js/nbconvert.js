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
