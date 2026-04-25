"""``ContentPageBox`` — a :class:`Content` block representing exactly one logical page.

The page-box is the foundational primitive behind the WYSIWYG authoring
story (see :class:`nbprint.NBPrintPage`). It is a plain pydantic
:class:`Content` subclass so every field — including the inherited
``content`` list of children, ``style``, ``css``, ``classname``,
``attrs`` — is reachable through hydra/lerna CLI overrides such as::

    +nbprint.content.middlematter[3].fit=strict
    +nbprint.content.middlematter[3].page_orientation=landscape
    +nbprint.content.middlematter[3].css=":scope { background: red; }"

No new sectioning semantics are introduced: a ``ContentPageBox`` lives
inside whatever section owns the cell that produced it.

Key guarantees (enforced by CSS + later JS preprocessing passes):

* A page-box always produces *at least one* page (no blank-page removal
  sweeps it away — see :mod:`postprocessing/validate.js`).
* A page-box ends with a hard page break; following content always
  starts on a fresh page.
* Overflowing content flows to additional pages — children are never
  silently dropped.
"""

from __future__ import annotations

from typing import Literal

from IPython.display import HTML
from pydantic import Field, model_validator

from nbprint.config.common import PageOrientation, PageSize

from ._layout_presets import PAGE_BOX_BASE_CSS, PageBoxLayout, build_page_box_css
from .base import Content
from .page_block import ContentPageBlock

__all__ = ("ContentPageBox", "PageBoxFit", "PageBoxLayout")


PageBoxFit = Literal["scale", "shrink", "strict", "none"]


def _extract_grid_template_areas(template: str) -> set[str]:
    """Pull the set of area names from a CSS ``grid-template`` value.

    The ``grid-template`` shorthand interleaves quoted row strings (the
    area names) with track sizes and a ``/`` separator. Non-area tokens
    (``.`` placeholders, sizes, fractions, the ``/`` itself) are
    discarded. Empty quotes parse to no areas, which is fine.

    Robust to:
      * single or double quotes
      * multi-row templates (``"a a" "b c"``)
      * track sizes interleaved (``"a a" 1fr "b c" 2fr / 1fr 1fr``)
      * the ``.`` placeholder (denotes an empty cell)
    """
    import re

    quoted = re.findall(r"['\"]([^'\"]*)['\"]", template)
    areas: set[str] = set()
    for row in quoted:
        for token in row.split():
            if token and token != ".":  # noqa: S105 - "token" here is a CSS grid area name, not a credential
                areas.add(token)
    return areas


# Default CSS: force page breaks around the box, fill the page vertically
# so empty or near-empty boxes still render a full page (at-least-one-page
# guarantee), and allow children to break inside when overflowing to the
# next page.
_DEFAULT_PAGE_BOX_CSS = PAGE_BOX_BASE_CSS


class ContentPageBox(Content):
    """A :class:`Content` block representing a single logical page.

    The box is a regular pydantic model: author it in YAML, override it
    from the CLI, or produce it at runtime via :class:`NBPrintPage`.
    """

    fit: PageBoxFit = Field(
        default="scale",
        description=(
            "How to handle content that doesn't fit on one page. "
            "'scale' (default): shrink scalable children — images, SVGs, "
            "Plotly charts, tables — to fit; text is never shrunk. "
            "'shrink': same as 'scale' but with a tighter budget. "
            "'strict': no scaling; emit a render-time warning on overflow. "
            "'none': no composite measurement; children flow normally "
            "but the box still produces break-before/after page."
        ),
    )

    # Per-page overrides. When set, Phase 9.9 will emit a named @page
    # rule and route this box to it. Until that lands these fields
    # serialize through normally; downstream passes can read them.
    page_size: PageSize | None = Field(
        default=None,
        description="Per-box override for the document page size. Falls back to the global Page.size.",
    )
    page_orientation: PageOrientation | None = Field(
        default=None,
        description="Per-box override for the document page orientation.",
    )
    page_margins: str | None = Field(
        default=None,
        description="Per-box override for the document page margins (raw CSS `margin` value).",
    )

    min_pages: int = Field(
        default=1,
        ge=1,
        description="Minimum number of pages this box must produce. Guaranteed even when the box is empty.",
    )

    # ── Layout preset ────────────────────────────────────────────────
    # Each preset emits the corresponding CSS on ``:scope``; the
    # ``custom`` preset suppresses preset CSS so the user owns
    # ``:scope`` styling via the inherited ``css`` field.
    layout: PageBoxLayout = Field(
        default="flow",
        description=(
            "Built-in layout for child blocks. 'flow' (default): "
            "native block-flow. 'columns-2'/'columns-3': CSS multi-column. "
            "'grid-2x2'/'grid-3x2'/'grid-3x3': fixed grids. 'grid': bare "
            "`display: grid` — pair with `grid_template` (Phase 9.5) for "
            "named areas. 'flex-row'/'flex-column'/'inline': reuse the "
            "existing flex/inline layout containers' CSS. 'masonry': "
            "native CSS masonry with a JS polyfill (Phase 9.17). "
            "'custom': suppress preset CSS — the user owns `:scope`."
        ),
    )
    gap: str | None = Field(
        default=None,
        description="CSS `gap` (or `column-gap` for the columns presets) between children.",
    )
    padding: str | None = Field(
        default=None,
        description="CSS `padding` applied to the page-box `:scope`.",
    )
    align: str | None = Field(
        default=None,
        description="CSS `align-items` for grid/flex presets (no-op for `flow`/`columns-*`/`custom`).",
    )
    justify: str | None = Field(
        default=None,
        description=("CSS `justify-items` (grid presets) or `justify-content` (flex presets). No-op for `flow`/`columns-*`/`custom`."),
    )
    grid_template: str | None = Field(
        default=None,
        description=(
            "Raw CSS `grid-template` value (e.g. `\"'hero hero' 'chart table' / 1fr 1fr\"`). "
            "Only meaningful when `layout='grid'`. Validator cross-checks "
            "that every `ContentPageBlock.area` referenced by children "
            "appears in the template; unused areas are allowed."
        ),
    )

    # Inherit ``content: str | list[Content] | None`` from ``Content``.
    # Runtime (NBPrintPage single-cell) use sets it to the cell source;
    # YAML use sets it to a list of child ``Content`` models.

    css: str = _DEFAULT_PAGE_BOX_CSS

    @model_validator(mode="after")
    def _populate_data_attrs(self) -> ContentPageBox:
        """Seed ``attrs`` and ``tags`` with page-box defaults, build the
        preset CSS, and auto-wrap bare child :class:`Content` into
        :class:`ContentPageBlock` so the DOM shape is always
        ``page-box > block > <user content>``.

        Values already present in ``attrs`` win (so CLI overrides of
        ``attrs.data-nbprint-*`` take precedence). Mutates in place to
        avoid re-triggering ``validate_assignment``.
        """
        if "nbprint:content:page-box" not in self.tags:
            self.tags.append("nbprint:content:page-box")
        if self.attrs is None:
            object.__setattr__(self, "attrs", {})
        attrs = self.attrs  # type: ignore[assignment]
        attrs.setdefault("data-nbprint-page-box", self._id)
        attrs["data-nbprint-fit"] = str(self.fit)
        attrs["data-nbprint-layout"] = self.layout
        if self.min_pages > 1:
            attrs.setdefault("data-nbprint-min-pages", str(self.min_pages))

        # Build preset CSS unless the user has supplied a non-default
        # ``css`` value (which fully overrides — opt-out for power
        # users). When ``layout='custom'`` the base CSS is preserved
        # but no preset rules are appended, so the user's ``:scope``
        # additions win cleanly.
        if self.css in {_DEFAULT_PAGE_BOX_CSS, PAGE_BOX_BASE_CSS}:
            preset_css = build_page_box_css(
                self.layout,
                gap=self.gap,
                padding=self.padding,
                align=self.align,
                justify=self.justify,
            )
            # When ``grid_template`` is set, append a ``grid-template``
            # declaration. We don't gate on ``layout='grid'`` because
            # ``grid-template`` is harmless for non-grid layouts (the
            # browser ignores it) and gating would surprise users who
            # try ``layout='grid-2x2'`` + ``grid_template``.
            if self.grid_template is not None:
                preset_css += f":scope {{ grid-template: {self.grid_template}; }}\n"
            object.__setattr__(self, "css", preset_css)

        # Cross-check: every referenced area in child blocks must
        # appear in ``grid_template``. Unused template areas are
        # allowed (empty cells). Skipped when ``grid_template`` is
        # ``None`` (no constraint) or when the user supplied a custom
        # ``css`` (we don't know what areas it defines).
        if self.grid_template is not None and isinstance(self.content, list):
            template_areas = _extract_grid_template_areas(self.grid_template)
            for child in self.content:
                if not isinstance(child, ContentPageBlock):
                    continue
                if child.area is not None and child.area not in template_areas:
                    msg = (
                        f"ContentPageBox.grid_template does not define "
                        f"area '{child.area}' referenced by child block "
                        f"'{child._id}'. Defined areas: "
                        f"{sorted(template_areas) or '<none>'}"
                    )
                    raise ValueError(msg)

        # Auto-wrap any bare child Content into a ContentPageBlock so
        # downstream layout passes can rely on a uniform DOM shape.
        # Strings (single-cell runtime use) and existing blocks pass
        # through unchanged.
        if isinstance(self.content, list):
            wrapped: list = []
            for child in self.content:
                if isinstance(child, ContentPageBlock):
                    wrapped.append(child)
                elif isinstance(child, Content):
                    wrapped.append(ContentPageBlock(content=[child]))
                else:
                    # Non-Content payload (shouldn't happen via normal
                    # construction); pass through to surface the issue
                    # downstream rather than silently mangle it.
                    wrapped.append(child)
            object.__setattr__(self, "content", wrapped)

        return self

    def __call__(self, **_) -> HTML:
        # Children are nested into the wrapper by the nbprint runtime
        # via ``data-nbprint-parent-id``; no source-level HTML needed.
        return HTML("")
