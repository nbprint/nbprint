"""Runtime API for declaring a WYSIWYG page-box inside a notebook cell.

:class:`NBPrintPage` mirrors :class:`nbprint.NBPrintCell`: it emits a
hidden ``display()`` output carrying a custom MIME type, which the
ingestion path converts into a real :class:`ContentPageBox` at load
time.

Usage (single-cell mode)::

    from nbprint import NBPrintPage

    # Default: shrink scalable children to fit one page; overflow flows.
    with NBPrintPage():
        display(summary_table)
        display(pnl_chart)

    # Landscape override with strict overflow detection
    with NBPrintPage(page_orientation="landscape", fit="strict"):
        display(wide_dashboard)

The runtime API is a convenience for notebook authors. A YAML / CLI
user can author the equivalent :class:`ContentPageBox` directly and
never invoke ``NBPrintPage``.

Multi-cell mode (wrapping several subsequent cells into one page box)
is planned for a follow-up task; single-cell wrapping is the MVP.
"""

from __future__ import annotations

import json
from typing import Any

from IPython.display import display
from typing_extensions import Self

from nbprint.config.common import PageOrientation, PageSize, Style
from nbprint.config.content.page_box import PageBoxFit, PageBoxLayout

__all__ = ("NBPRINT_PAGE_MIME", "NBPrintPage")

NBPRINT_PAGE_MIME = "application/nbprint.page+json"

# Fully qualified target path used by ingestion to construct the right
# Content subclass. Kept here to avoid an import-time circular.
_PAGE_BOX_TYPE = "nbprint.ContentPageBox"


class NBPrintPage:
    """Runtime helper that marks the current cell as a ``ContentPageBox``.

    Parameters
    ----------
    section : str | None
        Target document section (e.g. ``"covermatter"``). Routed through
        the same mechanism as :class:`NBPrintCell`.
    fit : {"scale", "shrink", "strict", "none"}
        How to handle overflow. See :class:`ContentPageBox` for details.
    page_size : PageSize | str | None
        Per-box override of the document page size.
    page_orientation : PageOrientation | str | None
        Per-box override of the document page orientation.
    page_margins : str | None
        Per-box override of the document page margins (raw CSS value).
    min_pages : int
        Minimum number of pages this box produces. Default ``1``.
    css : str | None
        Extra CSS to merge into the box (e.g. background, padding).
    style : Style | None
        Structured ``Style`` object merged into the box's style.
    classname : str | list[str] | None
        Extra CSS class(es) for the box wrapper.
    attrs : dict[str, str] | None
        Extra HTML attributes for the box wrapper.
    ignore : bool | None
        If ``True``, hide the box from the final output.
    emit : bool
        If ``True`` (default) immediately publish the metadata via
        ``display()``. Set to ``False`` when you only want to use the
        object as a context manager; metadata is emitted on ``__enter__``.

    """

    def __init__(
        self,
        *,
        section: str | None = None,
        fit: PageBoxFit = "scale",
        page_size: PageSize | str | None = None,
        page_orientation: PageOrientation | str | None = None,
        page_margins: str | None = None,
        min_pages: int = 1,
        layout: PageBoxLayout = "flow",
        gap: str | None = None,
        padding: str | None = None,
        align: str | None = None,
        justify: str | None = None,
        css: str | None = None,
        style: Style | None = None,
        classname: str | list[str] | None = None,
        attrs: dict[str, str] | None = None,
        ignore: bool | None = None,
        emit: bool = True,
    ) -> None:
        self.section = section
        self.fit = fit
        self.page_size = page_size
        self.page_orientation = page_orientation
        self.page_margins = page_margins
        self.min_pages = min_pages
        self.layout = layout
        self.gap = gap
        self.padding = padding
        self.align = align
        self.justify = justify
        self.css = css
        self.style = style
        self.classname = classname
        self.attrs = attrs
        self.ignore = ignore
        self._emitted = False

        if emit:
            self._emit()

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dict of fields to merge into the cell model.

        Always includes ``type_`` so the ingestion path constructs a
        :class:`ContentPageBox` rather than a plain :class:`Content`.
        """
        d: dict[str, Any] = {
            "type_": _PAGE_BOX_TYPE,
            "fit": self.fit,
            "min_pages": self.min_pages,
            "layout": self.layout,
        }
        if self.section is not None:
            d["section"] = self.section
        if self.page_size is not None:
            d["page_size"] = str(self.page_size)
        if self.page_orientation is not None:
            d["page_orientation"] = str(self.page_orientation)
        if self.page_margins is not None:
            d["page_margins"] = self.page_margins
        if self.gap is not None:
            d["gap"] = self.gap
        if self.padding is not None:
            d["padding"] = self.padding
        if self.align is not None:
            d["align"] = self.align
        if self.justify is not None:
            d["justify"] = self.justify
        if self.css is not None:
            d["css"] = self.css
        if self.style is not None:
            d["style"] = self.style.model_dump(mode="json", exclude_none=True)
        if self.classname is not None:
            d["classname"] = self.classname
        if self.attrs is not None:
            d["attrs"] = self.attrs
        if self.ignore is not None:
            d["ignore"] = self.ignore
        return d

    def _emit(self) -> None:
        if self._emitted:
            return
        data = {NBPRINT_PAGE_MIME: json.dumps(self.to_dict())}
        display(data, raw=True)
        self._emitted = True

    def __enter__(self) -> Self:
        if not self._emitted:
            self._emit()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return None
