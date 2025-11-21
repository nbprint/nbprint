import { initializeNBPrint } from "./nbprint";
import { createToc } from "./components/table-of-content";
import "@fortawesome/fontawesome-free/js/all";

let nbprint = initializeNBPrint();

document.addEventListener("DOMContentLoaded", async () => {
  // Process with NBPrint

  await nbprint.process();

  if (nbprint.buildPagedJS()) {
    // Build pagedjs
    await nbprint.build();
  } else {
    createToc({
      content: document.querySelector("body.jp-Notebook").querySelector("main"),
      tocElement: "#toc",
      titleElements: ["h1", "h2", "h3", "h4"],
    });
  }

  await nbprint.postprocess();
});
