/*!
 * fuma — theme toggle, mobile sidebar, TOC scroll spy and search dialog.
 */

(function () {
  "use strict";

  var body = document.body;
  var docEl = document.documentElement;

  document.querySelectorAll(".fd-llms").forEach(function (menu) {
    document.addEventListener("click", function (event) {
      if (!menu.contains(event.target) || event.target.closest("a")) menu.open = false;
    });
    menu.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && menu.open) {
        menu.open = false;
        menu.querySelector("summary").focus();
        event.preventDefault();
      }
    });
  });

  /* Theme -------------------------------------------------------------- */

  function isDark() {
    if (docEl.classList.contains("dark")) return true;
    if (docEl.classList.contains("light")) return false;
    return matchMedia("(prefers-color-scheme: dark)").matches;
  }

  var themeOptions = document.querySelectorAll(".fd-theme-option");

  function syncThemeSwitch() {
    var mode = isDark() ? "dark" : "light";
    themeOptions.forEach(function (option) {
      option.dataset.active = String(option.dataset.fdTheme === mode);
    });
  }

  function applyTheme(dark) {
    docEl.classList.toggle("dark", dark);
    docEl.classList.toggle("light", !dark);
    docEl.style.colorScheme = dark ? "dark" : "light";
    try {
      localStorage.setItem("fuma-theme", dark ? "dark" : "light");
    } catch (e) {}
    syncThemeSwitch();
  }

  themeOptions.forEach(function (option) {
    option.addEventListener("click", function () {
      applyTheme(option.dataset.fdTheme === "dark");
    });
  });
  syncThemeSwitch();

  document.querySelectorAll(".fd-theme-toggle").forEach(function (button) {
    button.addEventListener("click", function () {
      applyTheme(!isDark());
    });
  });

  /* Mobile sidebar ----------------------------------------------------- */

  var sidebar = document.getElementById("fd-sidebar");
  var scrim = document.querySelector(".fd-sidebar-scrim");
  var sidebarToggle = document.querySelector(".fd-sidebar-toggle");

  function setSidebar(open) {
    if (!sidebar) return;
    sidebar.dataset.open = open ? "true" : "false";
    if (sidebarToggle) sidebarToggle.setAttribute("aria-expanded", String(open));
    if (scrim) scrim.hidden = !open;
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", function () {
      setSidebar(sidebar.dataset.open !== "true");
    });
  }
  if (scrim) scrim.addEventListener("click", function () { setSidebar(false); });
  setSidebar(false);

  /* Desktop sidebar collapse ------------------------------------------- */

  function setCollapsed(collapsed) {
    if (collapsed) docEl.dataset.sidebarCollapsed = "true";
    else delete docEl.dataset.sidebarCollapsed;
    try {
      localStorage.setItem("fuma-sidebar", collapsed ? "collapsed" : "expanded");
    } catch (e) {}
  }

  document.querySelectorAll(".fd-sidebar-collapse").forEach(function (button) {
    button.addEventListener("click", function () { setCollapsed(true); });
  });
  var restore = document.getElementById("fd-sidebar-restore");
  if (restore) restore.addEventListener("click", function () { setCollapsed(false); });

  var tocCollapse = document.querySelector(".fd-toc-collapse");
  var tocRestore = document.getElementById("fd-toc-restore");
  function setTocCollapsed(collapsed) {
    if (collapsed) docEl.dataset.tocCollapsed = "true";
    else delete docEl.dataset.tocCollapsed;
    try {
      localStorage.setItem("fuma-toc", collapsed ? "collapsed" : "expanded");
    } catch (e) {}
    (collapsed ? tocRestore : tocCollapse).focus();
    if (!collapsed) requestAnimationFrame(drawRail);
  }
  if (tocCollapse) tocCollapse.addEventListener("click", function () { setTocCollapsed(true); });
  if (tocRestore) tocRestore.addEventListener("click", function () { setTocCollapsed(false); });

  /* Keep the active sidebar entry in view ------------------------------ */

  var current = sidebar && sidebar.querySelector(".fd-link.fd-current");
  if (current) {
    var scroller = sidebar.querySelector(".fd-sidebar-nav") || sidebar;
    var top = current.offsetTop - scroller.clientHeight / 2;
    if (top > 0) scroller.scrollTop = top;
  }

  /* TOC popover -------------------------------------------------------- */

  var tocTrigger = document.querySelector(".fd-toc-trigger");
  var tocMobile = document.getElementById("fd-toc-mobile");
  if (tocTrigger && tocMobile) {
    tocTrigger.addEventListener("click", function () {
      var open = tocTrigger.getAttribute("aria-expanded") === "true";
      tocTrigger.setAttribute("aria-expanded", String(!open));
      tocMobile.hidden = open;
    });
    tocMobile.addEventListener("click", function (event) {
      if (event.target.closest("a")) {
        tocTrigger.setAttribute("aria-expanded", "false");
        tocMobile.hidden = true;
      }
    });
  }

  /* TOC scroll spy ----------------------------------------------------- */

  var tocNav = document.getElementById("fd-toc");
  var tocItems = tocNav ? Array.prototype.slice.call(tocNav.querySelectorAll(".fd-toc-item")) : [];
  var rail = tocNav && tocNav.querySelector(".fd-toc-rail");
  var track = rail && rail.querySelector(".fd-toc-track");
  var thumb = rail && rail.querySelector(".fd-toc-thumb");

  var RAIL_INDENT = 6;
  var RAIL_BASE = 6;
  var RAIL_CURVE = 10;

  // A single path that steps sideways as heading depth changes, so the rail
  // traces the outline of the list rather than running straight down.
  function railPath() {
    if (!tocItems.length) return "";
    var x = function (item) { return RAIL_BASE + (Number(item.dataset.depth || 1) - 1) * RAIL_INDENT; };
    var d = "";
    var prevX = x(tocItems[0]);
    d += "M" + prevX + " 0";
    tocItems.forEach(function (item) {
      var link = item.querySelector("a");
      var top = link.offsetTop;
      var bottom = top + link.offsetHeight;
      var nextX = x(item);
      if (nextX !== prevX) {
        var mid = top + RAIL_CURVE;
        d += " L" + prevX + " " + top;
        d += " C" + prevX + " " + mid + " " + nextX + " " + (mid - RAIL_CURVE / 2) + " " + nextX + " " + mid;
        prevX = nextX;
      }
      d += " L" + nextX + " " + bottom;
    });
    return d;
  }

  function drawRail() {
    if (!rail || !tocItems.length) return;
    var d = railPath();
    track.setAttribute("d", d);
    thumb.setAttribute("d", d);
    var host = rail.parentElement;
    rail.setAttribute("viewBox", "0 0 " + rail.clientWidth + " " + host.scrollHeight);
    rail.setAttribute("height", host.scrollHeight);
  }

  if (tocItems.length) {
    var targets = tocItems
      .map(function (item) {
        var href = item.querySelector("a").getAttribute("href") || "";
        var anchor = href.charAt(0) === "#" ? document.getElementById(decodeURIComponent(href.slice(1))) : null;
        var heading = anchor && (anchor.matches("h1, h2, h3, h4, h5, h6") ? anchor : anchor.querySelector("h1, h2, h3, h4, h5, h6") || anchor);
        return heading ? { item: item, heading: heading } : null;
      })
      .filter(Boolean);

    // The thumb spans every heading currently on screen, not just the first.
    var mark = function (active) {
      tocItems.forEach(function (item) {
        item.classList.remove("fd-active");
      });
      if (!active.length) return;
      active.forEach(function (entry) {
        entry.item.classList.add("fd-active");
      });
      if (rail) {
        var first = active[0].item.querySelector("a");
        var last = active[active.length - 1].item.querySelector("a");
        thumb.style.setProperty("--fd-track-top", first.offsetTop + "px");
        thumb.style.setProperty("--fd-track-bottom", last.offsetTop + last.offsetHeight + "px");
      }
    };

    drawRail();
    addEventListener("resize", drawRail);

    var visible = new Set();
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) visible.add(entry.target);
          else visible.delete(entry.target);
        });
        var active = targets.filter(function (target) {
          return visible.has(target.heading);
        });
        if (!active.length) {
          var viewTop = entries[0] && entries[0].rootBounds ? entries[0].rootBounds.top : 0;
          var fallback = null;
          var fallbackDistance = Infinity;
          targets.forEach(function (target) {
            var distance = Math.abs(target.heading.getBoundingClientRect().top - viewTop);
            if (distance < fallbackDistance) {
              fallback = target;
              fallbackDistance = distance;
            }
          });
          if (fallback) active = [fallback];
        }
        mark(active);
      },
      { threshold: 0.9 }
    );

    targets.forEach(function (target) {
      observer.observe(target.heading);
    });
  }

  /* Search ------------------------------------------------------------- */
  // Scoring and index loading live in sphinx-searchlite; this is only the UI.

  var dialog = document.getElementById("fd-search-dialog");
  if (!dialog || typeof dialog.showModal !== "function" || !window.SearchLite) return;

  var input = document.getElementById("fd-search-input");
  var results = document.getElementById("fd-search-results");
  var empty = document.getElementById("fd-search-empty");
  var engine = window.SearchLite.create({ url: window.SearchLite.indexUrl });
  var selected = 0;

  function render(found) {
    results.replaceChildren();
    found.items.forEach(function (record, position) {
      var link = document.createElement("a");
      link.className = "fd-search-result";
      link.href = record.u;
      link.setAttribute("role", "option");
      link.setAttribute("aria-selected", String(position === selected));

      var title = document.createElement("span");
      title.className = "fd-search-result-title";
      title.appendChild(window.SearchLite.highlight(record.s || record.t, found.terms));

      var context = document.createElement("span");
      context.className = "fd-search-result-context";
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
    var options = results.querySelectorAll(".fd-search-result");
    if (!options.length) return;
    selected = (selected + delta + options.length) % options.length;
    options.forEach(function (option, position) {
      option.setAttribute("aria-selected", String(position === selected));
    });
    options[selected].scrollIntoView({ block: "nearest" });
  }

  function open() {
    if (dialog.open) return;
    dialog.showModal();
    engine.load().then(update);
    input.focus();
    input.select();
  }

  document.querySelectorAll("[data-fd-search-open]").forEach(function (trigger) {
    trigger.addEventListener("click", open);
  });

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
      var active = results.querySelector('.fd-search-result[aria-selected="true"]');
      if (active) {
        event.preventDefault();
        window.location.href = active.href;
      }
    } else if (event.key === "Escape") {
      // `<input type=search>` swallows the first Escape to clear itself, which
      // would leave the dialog needing two presses despite the `Esc` hint.
      event.preventDefault();
      dialog.close();
    }
  });

  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) dialog.close();
  });

  document.addEventListener("keydown", function (event) {
    var target = event.target;
    var typing = target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable);
    if (typing) return;
    if (event.key === "/" || ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k")) {
      event.preventDefault();
      open();
    }
  });
})();
