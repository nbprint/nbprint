export * from "./components/table-of-content";
import { createToc } from "./components/table-of-content";
import { Previewer, registerHandlers, Handler } from "pagedjs";
import "@fortawesome/fontawesome-free/js/all";

export class handlers extends Handler {
  constructor(chunker, polisher, caller) {
    super(chunker, polisher, caller);
  }

  beforeParsed(content) {
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
