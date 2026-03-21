# Granular Section Configuration — Roadmap

**Branch:** `tkp/details`
**Goal:** Allow more granular configuration of document sections (cover, frontmatter, chapters, endmatter, etc.) with per-section page layout overrides.

## What's been done

Initial commit (`6d72cce`) introduced the structural model. Subsequent work wired up all plumbing and implemented section-aware generation.

- **`Section` literal type** — 13-value `Literal` covering the full document structure from `prematter` through `rearmatter`.
- **Expanded `ContentMarshall`** — from 4 fields to 13 granular section fields, with private per-group aggregation attributes, `sections()` iterator, and `SECTION_ORDER`/`SECTION_GROUPS` constants.
- **`PageGlobal` subclass of `Page`** — holds `size`/`orientation` and a `pages: dict[Section, Page]` for per-section page overrides; generates `@page sectionName` CSS rules.
- **Moved `page.py` into `config/core/`** — co-locates with the rest of the core config.
- **Section-aware `Configuration.generate()`** — iterates by section, tags cells with `nbprint:section:{name}` and `nbprint:section-group:{group}`.
- **Per-section page CSS** — `PageGlobal.render()` generates named page rules and element selectors for Paged.js.
- **`counter_reset` / `counter_style`** — per-section page numbering control (e.g., roman numerals for frontmatter).

## Phase 1 — Wire up the plumbing ✅

- [x] **1.1 Fix `ContentMarshall._all` validator** — include all 13 sections in correct document order; populate private per-group attributes.
- [x] **1.2 Switch `Configuration.page` to `PageGlobal`** — update field type and validator; ensure backward compat with existing region-only configs.
- [x] **1.3 Verify `_convert_content_from_dict`** — confirm it handles all 13 section keys when hydrating from YAML/dict.
- [x] **1.4 Unit tests** — `Section` literal, `ContentMarshall` with content in various sections, `PageGlobal` with per-section overrides, backward compat with list-only content.

## Phase 2 — Section-aware generation ✅

- [x] **2.1 Section-aware `Configuration.generate()`** — iterate by section group instead of flat `content.all`; inject section-boundary metadata/tags.
- [x] **2.2 Per-section page style application** — look up `page.pages[section]` during generation to apply section-specific page regions/CSS.
- [x] **2.3 CSS generation for named pages** — generate `@page sectionName { ... }` rules and `[data-nbprint-section]` element attributes for Paged.js.

## Phase 3 — User-facing config & examples ✅

- [x] **3.1 YAML example: structured sections** — `examples/sections.yaml` using dict-style `content:` with section keys and per-section page overrides.
- [x] **3.2 Hydra config example** — `examples/hydra/content/sections.yaml` for section-level content overrides.
- [x] **3.3 Documentation** — updated `docs/src/configuration.md` with section model, `Section` values, and per-section page customization examples.

## Phase 4 — Advanced features (partial)

- [ ] **4.1 `middlematter_separators` interleaving** — support list-of-lists middlematter with chapter separator/title pages. Requires schema change to support nested content lists; separators currently render as a standalone section in document order.
- [ ] **4.2 Auto table of contents** — optionally auto-generate TOC from middlematter headings when `table_of_contents` is declared but empty. Users can currently place `ContentTableOfContents` in the `table_of_contents` section explicitly.
- [x] **4.3 Page numbering per section** — `counter_reset` and `counter_style` fields on `Page`, used in per-section CSS generation (e.g., `counter(page, lower-roman)`).

## Housekeeping ✅

- [x] **Migrate hydra → lerna** — replaced all `from hydra` imports with `from lerna` equivalents; removed `hydra-core` from `pyproject.toml` dependencies. Lerna is a drop-in replacement with the same API.
