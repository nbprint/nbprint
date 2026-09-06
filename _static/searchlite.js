/*!
 * sphinx-searchlite — BM25 search over a JSON index, no dependencies.
 *
 * Public API:
 *   var engine = SearchLite.create({ url });
 *   engine.load().then(function () { engine.search("query"); });
 *
 * `search` returns { items, terms }. `terms` includes prefix expansions so a
 * caller can highlight what actually matched.
 */

(function (global) {
  "use strict";

  var K1 = 1.2;
  var B = 0.75;
  var HEADING_BOOST = 8;
  var PAGE_BOOST = 1.5;
  var SECTION_BONUS = 1.1;
  var MAX_PREFIX_TERMS = 16;
  var MAX_RESULTS = 20;

  function tokenize(text) {
    return String(text || "").toLowerCase().match(/[a-z0-9_]+/g) || [];
  }

  function build(records) {
    var df = Object.create(null);
    var postings = Object.create(null);
    var headings = Object.create(null);
    var pages = Object.create(null);
    var lengths = new Array(records.length);
    var total = 0;

    records.forEach(function (record, i) {
      var bodyTerms = tokenize(record.x);
      // Page-level records have no section heading, so their title is the heading.
      var headingTerms = tokenize(record.s || record.t);
      var pageTerms = tokenize(record.t);
      lengths[i] = bodyTerms.length || 1;
      total += lengths[i];

      var frequencies = Object.create(null);
      bodyTerms.forEach(function (term) {
        frequencies[term] = (frequencies[term] || 0) + 1;
      });

      var note = function (bucket, term) {
        if (!bucket[term]) bucket[term] = Object.create(null);
        bucket[term][i] = true;
        // Keep heading-only words reachable even when absent from the body.
        if (!(term in frequencies)) frequencies[term] = 0;
      };
      headingTerms.forEach(function (term) {
        note(headings, term);
      });
      pageTerms.forEach(function (term) {
        note(pages, term);
      });

      Object.keys(frequencies).forEach(function (term) {
        if (!postings[term]) {
          postings[term] = [];
          df[term] = 0;
        }
        postings[term].push([i, frequencies[term]]);
        df[term] += 1;
      });
    });

    return {
      records: records,
      count: records.length,
      df: df,
      postings: postings,
      headings: headings,
      pages: pages,
      lengths: lengths,
      average: total / (records.length || 1),
      terms: Object.keys(postings).sort(),
    };
  }

  // The trailing token is still being typed, so match it as a prefix as well as
  // exactly: typing "install" should also reach "installation".
  function expand(index, term, isLast) {
    var variants = index.postings[term] ? [term] : [];
    if (!isLast || term.length < 2) return variants;
    for (var i = 0; i < index.terms.length && variants.length < MAX_PREFIX_TERMS; i++) {
      if (index.terms[i] !== term && index.terms[i].lastIndexOf(term, 0) === 0) variants.push(index.terms[i]);
    }
    return variants;
  }

  function rank(index, queryTerms) {
    var scores = Object.create(null);
    var hits = Object.create(null);
    var matched = [];
    var required = 0;

    queryTerms.forEach(function (term, position) {
      var variants = expand(index, term, position === queryTerms.length - 1);
      if (!variants.length) return;
      required += 1;
      variants.forEach(function (variant) {
        matched.push(variant);
        var frequency = index.df[variant];
        var idf = Math.log(1 + (index.count - frequency + 0.5) / (frequency + 0.5));
        index.postings[variant].forEach(function (posting) {
          var doc = posting[0];
          var tf = posting[1];
          var norm = (tf * (K1 + 1)) / (tf + K1 * (1 - B + (B * index.lengths[doc]) / index.average));
          var score = idf * norm;
          if (index.headings[variant] && index.headings[variant][doc]) score += idf * HEADING_BOOST;
          if (index.pages[variant] && index.pages[variant][doc]) score += idf * PAGE_BOOST;
          scores[doc] = (scores[doc] || 0) + score;
          if (!hits[doc]) hits[doc] = Object.create(null);
          hits[doc][position] = true;
        });
      });
    });

    if (!required) return { items: [], terms: [] };

    var items = Object.keys(scores)
      // Every query word must appear somewhere, so extra words narrow results.
      .filter(function (doc) {
        return Object.keys(hits[doc]).length === required;
      })
      .map(function (doc) {
        var record = index.records[Number(doc)];
        return { record: record, score: record.s ? scores[doc] * SECTION_BONUS : scores[doc] };
      })
      .sort(function (a, b) {
        return b.score - a.score;
      })
      .slice(0, MAX_RESULTS)
      .map(function (entry) {
        return entry.record;
      });

    return { items: items, terms: matched };
  }

  function excerpt(record, terms, length) {
    var size = length || 120;
    var text = record.x || "";
    var lower = text.toLowerCase();
    var at = -1;
    for (var i = 0; i < terms.length && at < 0; i++) at = lower.indexOf(terms[i]);
    if (at < 0) return text.slice(0, size);
    var start = Math.max(0, at - 40);
    return (start > 0 ? "\u2026" : "") + text.slice(start, start + size);
  }

  function highlight(text, terms) {
    var fragment = document.createDocumentFragment();
    var lower = text.toLowerCase();
    var cursor = 0;
    while (cursor < text.length) {
      var best = -1;
      var length = 0;
      terms.forEach(function (term) {
        var at = lower.indexOf(term, cursor);
        if (at !== -1 && (best === -1 || at < best)) {
          best = at;
          length = term.length;
        }
      });
      if (best === -1) {
        fragment.appendChild(document.createTextNode(text.slice(cursor)));
        break;
      }
      fragment.appendChild(document.createTextNode(text.slice(cursor, best)));
      var mark = document.createElement("mark");
      mark.textContent = text.slice(best, best + length);
      fragment.appendChild(mark);
      cursor = best + length;
    }
    return fragment;
  }

  function create(options) {
    var url = options.url;
    var index = null;
    var loading = null;

    return {
      load: function () {
        if (!loading) {
          loading = fetch(url)
            .then(function (response) {
              return response.ok ? response.json() : [];
            })
            .catch(function () {
              return [];
            })
            .then(function (records) {
              index = build(records);
              return index;
            });
        }
        return loading;
      },
      ready: function () {
        return index !== null;
      },
      search: function (query) {
        if (!index) return { items: [], terms: [] };
        var terms = tokenize(query);
        if (!terms.length) return { items: [], terms: [] };
        return rank(index, terms);
      },
    };
  }

  function resolveIndexUrl() {
    var script = document.currentScript || document.querySelector("script[data-searchlite-index]");
    if (!script) return null;
    return new URL(script.getAttribute("data-searchlite-index"), script.src).href;
  }

  global.SearchLite = {
    create: create,
    tokenize: tokenize,
    excerpt: excerpt,
    highlight: highlight,
    indexUrl: resolveIndexUrl(),
  };
})(window);
