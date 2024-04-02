import { initializeNBPrint } from "./nbprint";
import { build } from "./nbconvert";
import "@fortawesome/fontawesome-free/js/all";

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
