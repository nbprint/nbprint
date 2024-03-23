export * from "./components/table-of-content";
import { createToc } from "./components/table-of-content";
import { initializeNBPrint } from "./nbprint";
import { Previewer, registerHandlers, Handler } from "pagedjs";

class handlers extends Handler {
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

const build = async () => {
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

document.addEventListener("DOMContentLoaded", async () => {
  // Process with NBPrint
  let nbprint = initializeNBPrint();
  await nbprint.process();

  if (nbprint.buildPagedJS()) {
    // Build pagedjs
    if (window.voila_process !== undefined) {
      setTimeout(async () => {
        await build();
      }, 3000);
    } else {
      await build();
    }
  }

  await nbprint.postprocess();
});
