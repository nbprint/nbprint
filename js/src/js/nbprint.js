class NBPrint {
  constructor({ configuration, notebook_info }) {
    this._configuration = configuration;
    this._notebook_info = notebook_info;
  }

  async process() {
    document.querySelectorAll("[data-nbprint-parent-id]").forEach((elem) => {
      let parent_id = elem.getAttribute("data-nbprint-parent-id");
      let parent_elem = document.querySelector(
        `[data-nbprint-id="${parent_id}"`,
      );
      let place_to_insert = parent_elem.querySelector(".jp-RenderedHTML");
      if (place_to_insert && place_to_insert.lastElementChild) {
        place_to_insert.lastElementChild.appendChild(elem);
      } else if (place_to_insert) {
        place_to_insert.appendChild(elem);
      }
    });
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
