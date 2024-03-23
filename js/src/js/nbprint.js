class NBPrint {
  constructor({ configuration, notebook_info }) {
    this._configuration = configuration;
    this._notebook_info = notebook_info;
  }

  async process() {
    document.querySelectorAll("[data-nbprint-parent-id]").forEach((elem) => {
      // read the parent ID from the element
      let parent_id = elem.getAttribute("data-nbprint-parent-id");

      // grab the parent element
      let parent_elem = document.querySelector(
        `[data-nbprint-id="${parent_id}"`,
      );

      if (parent_elem) {
        parent_elem.appendChild(elem);
      }
    });
  }

  async postprocess() {
    const myEvent = new CustomEvent("nbprint-ready", {
      detail: {
        nbprint: this,
      },
      bubbles: true,
      cancelable: true,
      composed: false,
    });
    document.dispatchEvent(myEvent);
  }

  buildPagedJS() {
    return !this._configuration.debug;
  }
}

export function initializeNBPrint() {
  let nbp = new NBPrint({
    configuration: window._nbprint_configuration,
    notebook_info: window._nbprint_notebook_info,
  });

  // set global for use in templates
  window.NBPRINT = nbp;

  // alert in console for now
  console.debug("NBPrint Initialized!");
  return nbp;
}
