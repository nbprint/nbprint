/*!
 * sphinx-searchlite — the bundled dialog.
 *
 * Optional: set `searchlite_ui = False` and drive `window.SearchLite` yourself
 * if your theme ships its own search UI. The markup is created at runtime so
 * this works with any theme without template overrides.
 */

(function () {
  "use strict";

  if (!window.SearchLite || !window.SearchLite.indexUrl) return;

  // Captured while the script is executing; `currentScript` is null later on.
  var uiScript = document.currentScript || document.querySelector("script[data-searchlite-adopt]");
  var adoptThemeSearch = !uiScript || uiScript.getAttribute("data-searchlite-adopt") !== "false";

  var engine = window.SearchLite.create({ url: window.SearchLite.indexUrl });
  var selected = 0;

  var dialog = document.createElement("dialog");
  dialog.id = "searchlite-dialog";
  dialog.innerHTML =
    '<form class="searchlite-panel" method="dialog" role="search">' +
    '<div class="searchlite-field">' +
    '<input type="search" id="searchlite-input" autocomplete="off" spellcheck="false" placeholder="Search documentation…" aria-label="Search" />' +
    '<kbd class="searchlite-kbd">Esc</kbd>' +
    "</div>" +
    '<div id="searchlite-results" role="listbox" aria-label="Search results"></div>' +
    '<p id="searchlite-empty" class="searchlite-empty" hidden>No results found.</p>' +
    "</form>";
  document.body.appendChild(dialog);

  var input = dialog.querySelector("#searchlite-input");
  var results = dialog.querySelector("#searchlite-results");
  var empty = dialog.querySelector("#searchlite-empty");

  /* Colour adoption ------------------------------------------------------ */

  // Themes signal dark mode with their own class or attribute, not
  // `prefers-color-scheme`, so read the page's actual colours instead. The
  // computed value is assigned verbatim: it may be `color(display-p3 ...)` or
  // any other modern syntax, and parsing it would lose that.
  function backdropColour() {
    var node = document.body;
    while (node) {
      var colour = getComputedStyle(node).backgroundColor;
      if (colour && colour !== "transparent" && colour.indexOf("rgba(0, 0, 0, 0") !== 0) return colour;
      node = node.parentElement;
    }
    return null;
  }

  function adoptColours() {
    var background = backdropColour();
    var foreground = getComputedStyle(document.body).color;
    if (background) dialog.style.setProperty("--searchlite-background", background);
    if (foreground) dialog.style.setProperty("--searchlite-foreground", foreground);
  }

  // Theme toggles mutate a class or attribute on <html> or <body>.
  var themeWatcher = new MutationObserver(adoptColours);
  [document.documentElement, document.body].forEach(function (node) {
    themeWatcher.observe(node, { attributes: true, attributeFilter: ["class", "data-theme", "data-mode", "style"] });
  });
  adoptColours();

  function render(found) {
    results.replaceChildren();
    found.items.forEach(function (record, position) {
      var link = document.createElement("a");
      link.className = "searchlite-result";
      link.href = record.u;
      link.setAttribute("role", "option");
      link.setAttribute("aria-selected", String(position === selected));

      var title = document.createElement("span");
      title.className = "searchlite-result-title";
      title.appendChild(window.SearchLite.highlight(record.s || record.t, found.terms));

      var context = document.createElement("span");
      context.className = "searchlite-result-context";
      var summary = window.SearchLite.excerpt(record, found.terms);
      context.textContent = record.s ? record.t + " \u2014 " + summary : summary;

      link.append(title, context);
      results.appendChild(link);
    });
    empty.hidden = found.items.length > 0;
  }

  function update() {
    if (!input.value.trim()) {
      results.replaceChildren();
      empty.hidden = true;
      return;
    }
    selected = 0;
    render(engine.search(input.value));
  }

  function move(delta) {
    var options = results.querySelectorAll(".searchlite-result");
    if (!options.length) return;
    selected = (selected + delta + options.length) % options.length;
    options.forEach(function (option, position) {
      option.setAttribute("aria-selected", String(position === selected));
    });
    options[selected].scrollIntoView({ block: "nearest" });
  }

  function open() {
    if (dialog.open) return;
    adoptColours();
    dialog.showModal();
    engine.load().then(update);
    input.focus();
    input.select();
  }

  document.querySelectorAll("[data-searchlite-open]").forEach(function (trigger) {
    trigger.addEventListener("click", open);
  });

  /* Adopting the theme's own search box ---------------------------------- */

  // Without this the dialog has no visible entry point on a theme that knows
  // nothing about it, and the theme's box still leads to Sphinx's separate
  // search page — two searches with different results.
  function adoptSearchFields() {
    if (!adoptThemeSearch) return;
    var selectors = [
      'input[name="q"]',
      'form[action$="search.html"] input',
      'form[role="search"] input',
      "input[type=search]",
    ];
    var seen = new Set();
    selectors.forEach(function (selector) {
      document.querySelectorAll(selector).forEach(function (field) {
        if (field === input || seen.has(field)) return;
        seen.add(field);
        field.classList.add("searchlite-adopted");
        field.readOnly = true;
        field.addEventListener("focus", open);
        field.addEventListener("click", open);
        var form = field.closest("form");
        if (form) {
          form.addEventListener("submit", function (event) {
            event.preventDefault();
            open();
          });
        }
      });
    });
  }

  adoptSearchFields();

  input.addEventListener("input", function () {
    engine.load().then(update);
  });

  dialog.addEventListener("keydown", function (event) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      move(1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      move(-1);
    } else if (event.key === "Enter") {
      var active = results.querySelector('.searchlite-result[aria-selected="true"]');
      if (active) {
        event.preventDefault();
        window.location.href = active.href;
      }
    }
  });

  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) dialog.close();
  });

  document.addEventListener("keydown", function (event) {
    var target = event.target;
    if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) return;
    if (event.key === "/" || ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k")) {
      event.preventDefault();
      open();
    }
  });
})();
