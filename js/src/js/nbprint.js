import { build as buildpagedjs } from "./nbconvert";
import { preprocess } from "./preprocessing/measure";
import { postvalidate } from "./postprocessing/validate";

export class NBPrint {
  constructor({ configuration, notebook_info }) {
    this._configuration = configuration;
    ["outputs", "parameters", "page"].forEach((key) => {
      if (this._configuration[key] !== undefined) {
        // deserialize nested JSON
        this._configuration[key] = JSON.parse(this._configuration[key]);
      }
    });
    this._notebook_info = notebook_info;

    // Tracks render() promises registered by per-cell ESM scripts so
    // that build() can wait for every user-land render to complete
    // before handing off to pagedjs. Cell scripts call trackRender()
    // from within their nbprint-ready listener (see index.html.j2).
    this._renderPromises = [];
    this._renderPhaseComplete = false;
  }

  /**
   * Register an in-flight cell render with the nbprint lifecycle.
   *
   * Accepts either a Promise or a nullary function returning a Promise
   * (the latter is the ergonomic form for `trackRender(async () => {...})`).
   * Any rejection is caught and logged so one failing cell cannot block
   * pagination of the rest of the document.
   */
  trackRender(promiseOrThunk) {
    if (this._renderPhaseComplete) {
      // Late registration is accepted but logged — it will not block
      // pagedjs, and its effect on layout is undefined.
      console.warn(
        "[nbprint] trackRender() called after the ESM render phase completed; " +
          "DOM mutations may not be reflected in pagination.",
      );
    }
    const p =
      typeof promiseOrThunk === "function"
        ? Promise.resolve().then(() => promiseOrThunk())
        : Promise.resolve(promiseOrThunk);
    const guarded = p.catch((err) => {
      console.error("[nbprint] cell render failed:", err);
    });
    this._renderPromises.push(guarded);
    return guarded;
  }

  /**
   * Wait for every render registered via trackRender() to settle.
   * Resolves once the ESM render phase is complete; subsequent calls
   * are idempotent and resolve immediately.
   */
  async waitForRenders() {
    // Allow new promises to be registered while we await the current
    // batch — some renders schedule follow-up work synchronously.
    // Loop until a tick passes with no new entries.
    let settledCount = 0;
    while (settledCount < this._renderPromises.length) {
      const batch = this._renderPromises.slice(settledCount);
      settledCount = this._renderPromises.length;
      await Promise.allSettled(batch);
    }
    this._renderPhaseComplete = true;
  }

  async process() {
    // remap element hierarchy
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

    // hoist global styles
    let styles = Array.from(
      document.querySelector("main").querySelectorAll("style"),
    ).filter((val) => !val.textContent.includes("@scope"));
    for (let style of styles) {
      document.head.appendChild(style);
    }

    // Pre-pagination: measure and scale oversized content
    if (this.buildPagedJS()) {
      preprocess(document.querySelector("main"), this._configuration);
    }

    // Dispatch nbprint-ready: per-cell ESM listeners register their
    // render promises via trackRender() synchronously inside their
    // listener callback. CustomEvent dispatch is synchronous, so every
    // listener has run before dispatchEvent returns.
    const readyEvent = new CustomEvent("nbprint-ready", {
      detail: {
        nbprint: this,
      },
      bubbles: true,
      cancelable: true,
      composed: false,
    });
    document.dispatchEvent(readyEvent);

    // Barrier: wait for every registered cell render to settle before
    // returning. Callers (embedded.js) then proceed to build() with a
    // fully populated DOM.
    await this.waitForRenders();

    // Signal "all user-land ESM renders done; DOM is stable".
    // Pagination-adjacent code (measure tweaks, diagnostics) can
    // listen for this to run after all render() calls.
    const esmCompleteEvent = new CustomEvent("nbprint-esm-complete", {
      detail: {
        nbprint: this,
      },
      bubbles: true,
      cancelable: true,
      composed: false,
    });
    document.dispatchEvent(esmCompleteEvent);
  }

  async build() {
    await buildpagedjs(this._configuration);
    postvalidate(this._configuration);
  }

  async postprocess() {
    const myEvent = new CustomEvent("nbprint-done", {
      detail: {
        nbprint: this,
      },
      bubbles: true,
      cancelable: true,
      composed: false,
    });
    document.dispatchEvent(myEvent);
  }

  debug() {
    return this._configuration.debug;
  }

  buildPagedJS() {
    return (
      this._configuration.pagedjs !== false &&
      this._configuration.debug !== true
    );
  }
}

export function initializeNBPrint() {
  let nbp = new NBPrint({
    configuration: window._nbprint_configuration,
    notebook_info: window._nbprint_notebook_info,
  });

  // set global for use in templates
  window.NBPRINT = nbp;
  window._n = nbp;

  // alert in console for now
  console.debug("NBPrint Initialized!");

  // dispatch initialization event
  const myEvent = new CustomEvent("nbprint-initialized", {
    detail: {
      nbprint: nbp,
    },
    bubbles: true,
    cancelable: true,
    composed: false,
  });
  document.dispatchEvent(myEvent);

  // return object
  return nbp;
}
