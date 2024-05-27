import { initializeNBPrint } from "./nbprint";
import "@fortawesome/fontawesome-free/js/all";

let nbprint = initializeNBPrint();

document.addEventListener("DOMContentLoaded", async () => {
  // Process with NBPrint

  await nbprint.process();

  if (nbprint.buildPagedJS()) {
    // Build pagedjs
    await nbprint.build();
  }

  await nbprint.postprocess();
});
