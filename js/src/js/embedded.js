import { initializeNBPrint } from "./nbprint";
import { createToc } from "./components/table-of-content";
import "@fortawesome/fontawesome-free/js/all";

let nbprint = initializeNBPrint();

/**
 * Wait for every <img> in the document to finish decoding so that
 * naturalWidth/naturalHeight are populated before preprocessing and
 * pagination run. Without this, base64-encoded Jupyter output images
 * may still have a layout height of 0 when pagedjs measures, causing
 * them to overflow the page after decoding completes.
 */
async function waitForImages() {
  const imgs = Array.from(document.querySelectorAll("img"));
  await Promise.all(
    imgs.map((img) => {
      if (img.complete && img.naturalWidth > 0) return Promise.resolve();
      // decode() rejects on broken images; swallow so a single bad
      // image doesn't block the whole render.
      return (
        typeof img.decode === "function" ? img.decode() : Promise.resolve()
      ).catch(() => {
        // Fall back to a plain load-event wait if decode is unsupported
        return new Promise((resolve) => {
          if (img.complete) return resolve();
          img.addEventListener("load", resolve, { once: true });
          img.addEventListener("error", resolve, { once: true });
        });
      });
    }),
  );
}

document.addEventListener("DOMContentLoaded", async () => {
  // Ensure all <img> elements have valid natural dimensions before we
  // measure them or run pagedjs. Otherwise pagedjs sees zero-height
  // images and paginates around them incorrectly.
  await waitForImages();

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
