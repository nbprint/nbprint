"""``ContentPageBlock`` — the atomic layout item inside a :class:`ContentPageBox`.

A page-block is the unit a layout-aware page-box arranges. It is *not*
a layout container itself — that role is filled by
:class:`ContentFlexRowLayout`, :class:`ContentFlexColumnLayout`,
:class:`ContentInlineLayout`, and (forthcoming in Phase 9.4) the
``layout`` field on :class:`ContentPageBox`.

Use cases:

* Inside an ``NBPrintPage``: the page-box auto-wraps bare children in
  blocks (Phase 9.4) so every direct child of a page-box is a block.
  Authors who want to escape the auto-placement (e.g. "this hero spans
  both columns") instantiate a block explicitly with ``span=2``.
* Standalone (outside a page-box): the block's default
  ``break-inside: avoid`` makes it a useful "keep together"
  primitive for long-scroll reports.

Like :class:`ContentPageBox`, every field is a plain pydantic
attribute so hydra/lerna CLI overrides compose naturally::

    +nbprint.content.middlematter[0].content[2].span=2
    +nbprint.content.middlematter[0].content[2].aspect=1.7777
    +nbprint.content.middlematter[0].content[2].area=hero
"""

from __future__ import annotations

from typing import Literal

from IPython.display import HTML
from pydantic import Field, model_validator

from .base import Content

__all__ = ("BreakInside", "ContentPageBlock")


BreakInside = Literal["avoid", "auto"]


# Universal block CSS:
#   * min-width/min-height: 0 — required so flex/grid items can shrink
#     below their intrinsic content size (otherwise grid columns blow
#     out their tracks). This is a well-known grid/flex footgun.
#   * display: block — explicit, so the wrapper participates in flow
#     even when its content is inline.
# Per-instance values (break-inside, span, rows, area, aspect,
# min/max-height) are emitted as inline ``style=`` attributes via
# ``attrs`` so they apply with element-level specificity and override
# any preset CSS from the parent page-box.
_DEFAULT_PAGE_BLOCK_CSS = ":scope {\n  min-width: 0;\n  min-height: 0;\n  display: block;\n}\n"


def _format_aspect(value: float | str) -> str:
    """Normalize an ``aspect`` value into a CSS ``aspect-ratio`` string.

    Accepts:

    * ``float`` / ``int`` (e.g. ``1.7777``, ``16/9`` evaluated by Python)
    * ``"W:H"`` (e.g. ``"16:9"``) — the Pythonic shorthand.
    * Any other string — passed through verbatim, so authors can use the
      raw CSS forms ``"16/9"``, ``"16 / 9"``, or ``"auto 1 / 1"``.
    """
    if isinstance(value, (int, float)):
        return repr(float(value))
    if ":" in value:
        w, _, h = value.partition(":")
        return f"{w.strip()}/{h.strip()}"
    return value


class ContentPageBlock(Content):
    """A single layout item inside a :class:`ContentPageBox`.

    The block owns its own break behavior, optional grid positioning,
    and an optional aspect-ratio constraint. It does not itself produce
    a page break, never owns ``@page`` rules, and never measures its
    children — that's the page-box's job.
    """

    # ── Grid / column placement ──────────────────────────────────────
    span: int | None = Field(
        default=None,
        ge=1,
        description=(
            "Number of columns to span when the parent page-box uses a "
            "grid or columns layout. Maps to CSS `grid-column: span N`. "
            "``None`` means 1 column (auto-placement)."
        ),
    )
    rows: int | None = Field(
        default=None,
        ge=1,
        description=("Number of rows to span in a grid layout. Maps to CSS `grid-row: span N`. ``None`` means 1 row."),
    )
    area: str | None = Field(
        default=None,
        description=("Named grid area for use with ``ContentPageBox.layout='grid'`` and ``grid_template`` (Phase 9.5). Maps to CSS `grid-area`."),
    )

    # ── Sizing constraints ───────────────────────────────────────────
    aspect: float | str | None = Field(
        default=None,
        description=(
            "Aspect ratio constraint. Accepts a float (``1.7777``), a "
            "Pythonic shorthand (``'16:9'``), or a raw CSS value "
            "(``'16/9'``). Maps to CSS `aspect-ratio`."
        ),
    )
    min_height: str | None = Field(
        default=None,
        description="Optional CSS `min-height` for the block (e.g. `'4in'`).",
    )
    max_height: str | None = Field(
        default=None,
        description="Optional CSS `max-height` for the block (e.g. `'8in'`).",
    )

    # ── Pagination behavior ──────────────────────────────────────────
    break_inside: BreakInside = Field(
        default="avoid",
        description=(
            "CSS `break-inside` value. Default ``'avoid'`` keeps the "
            "block together on one page; set to ``'auto'`` to allow "
            "splitting (e.g. for long tables that should flow)."
        ),
    )

    # ── Measurement / scaling hints (consumed in 9.7 / 9.8) ──────────
    scalable: bool | None = Field(
        default=None,
        description=(
            "Whether this block's content can be proportionally shrunk "
            "by the page-box's `fit` pass. ``None`` (default) means "
            "auto-detect at render from the child output MIME types: "
            "True for images/SVGs/Plotly/tables, False for "
            "text/markdown/code. Set explicitly to override."
        ),
    )

    css: str = _DEFAULT_PAGE_BLOCK_CSS

    @model_validator(mode="after")
    def _populate_block_metadata(self) -> ContentPageBlock:
        """Seed ``tags`` and ``attrs`` with block defaults.

        Builds the inline ``style`` attribute from the per-instance
        sizing/placement fields. User-supplied ``style=`` in ``attrs``
        wins (we prepend, then preserve the user value).

        Mutates in place to avoid re-triggering ``validate_assignment``.
        """
        if "nbprint:content:page-block" not in self.tags:
            self.tags.append("nbprint:content:page-block")

        if self.attrs is None:
            object.__setattr__(self, "attrs", {})
        attrs = self.attrs  # type: ignore[assignment]

        # Discoverable data attributes — used by JS measurement passes
        # (9.7 / 9.8) and visual regression tests, and stable for
        # CSS attribute-selector targeting.
        attrs.setdefault("data-nbprint-block", self._id)
        attrs["data-nbprint-break-inside"] = self.break_inside
        if self.span is not None:
            attrs["data-nbprint-span"] = str(self.span)
        if self.rows is not None:
            attrs["data-nbprint-rows"] = str(self.rows)
        if self.area is not None:
            attrs["data-nbprint-area"] = self.area
        if self.scalable is not None:
            attrs["data-nbprint-scalable"] = "true" if self.scalable else "false"

        # Inline style — element-level specificity beats any page-box
        # preset CSS, so a per-block override always wins.
        rules: list[str] = [f"break-inside: {self.break_inside}"]
        if self.span is not None:
            rules.append(f"grid-column: span {self.span}")
        if self.rows is not None:
            rules.append(f"grid-row: span {self.rows}")
        if self.area is not None:
            rules.append(f"grid-area: {self.area}")
        if self.aspect is not None:
            rules.append(f"aspect-ratio: {_format_aspect(self.aspect)}")
        if self.min_height is not None:
            rules.append(f"min-height: {self.min_height}")
        if self.max_height is not None:
            rules.append(f"max-height: {self.max_height}")
        block_style = "; ".join(rules)

        # Preserve any user-supplied style by prepending ours.
        existing = attrs.get("style", "")
        if existing:
            attrs["style"] = f"{block_style}; {existing}"
        else:
            attrs["style"] = block_style

        return self

    def __call__(self, **_) -> HTML:
        # Children nest into the wrapper via ``data-nbprint-parent-id``;
        # no source-level HTML required.
        return HTML("")
