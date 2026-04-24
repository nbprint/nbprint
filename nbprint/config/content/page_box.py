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

from .base import Content

__all__ = ("ContentPageBox", "PageBoxFit")


PageBoxFit = Literal["scale", "shrink", "strict", "none"]


# Default CSS: force page breaks around the box, fill the page vertically
# so empty or near-empty boxes still render a full page (at-least-one-page
# guarantee), and allow children to break inside when overflowing to the
# next page.
_DEFAULT_PAGE_BOX_CSS = (
    ":scope {\n"
    "  break-before: page;\n"
    "  break-after: page;\n"
    "  break-inside: auto;\n"
    "  display: block;\n"
    "  min-height: var(--pagedjs-pagebox-min-height, 100%);\n"
    "}\n"
)


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

    # Inherit ``content: str | list[Content] | None`` from ``Content``.
    # Runtime (NBPrintPage single-cell) use sets it to the cell source;
    # YAML use sets it to a list of child ``Content`` models.

    css: str = _DEFAULT_PAGE_BOX_CSS

    @model_validator(mode="after")
    def _populate_data_attrs(self) -> ContentPageBox:
        """Seed ``attrs`` and ``tags`` with page-box defaults.

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
        if self.min_pages > 1:
            attrs.setdefault("data-nbprint-min-pages", str(self.min_pages))
        return self

    def __call__(self, **_) -> HTML:
        # Children are nested into the wrapper by the nbprint runtime
        # via ``data-nbprint-parent-id``; no source-level HTML needed.
        return HTML("")
