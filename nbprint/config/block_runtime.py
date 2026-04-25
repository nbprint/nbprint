"""Runtime API for declaring a WYSIWYG page-block inside a notebook cell.

:class:`NBPrintBlock` mirrors :class:`NBPrintPage`: it emits a hidden
``display()`` output carrying ``application/nbprint.block+json``,
which the ingestion path converts into a real
:class:`ContentPageBlock` at load time.

Usage (single-cell mode)::

    from nbprint import NBPrintBlock

    # Span 2 columns of a parent grid layout
    with NBPrintBlock(span=2, aspect="16:9"):
        display(hero_chart)

    # "Keep together" primitive — useful even outside a page-box
    with NBPrintBlock(break_inside="avoid"):
        display(summary_table)

    # Allow long content to flow across pages
    with NBPrintBlock(break_inside="auto"):
        display(very_long_dataframe)

The runtime API is a notebook-author convenience. A YAML / CLI user
can author the equivalent :class:`ContentPageBlock` directly.
"""

from __future__ import annotations

import json
from typing import Any

from IPython.display import display
from typing_extensions import Self

from nbprint.config.common import Style
from nbprint.config.content.page_block import BreakInside

__all__ = ("NBPRINT_BLOCK_MIME", "NBPrintBlock")

NBPRINT_BLOCK_MIME = "application/nbprint.block+json"

# Fully qualified target path used by ingestion to construct the right
# Content subclass. Kept here to avoid an import-time circular.
_PAGE_BLOCK_TYPE = "nbprint.ContentPageBlock"


class NBPrintBlock:
    """Runtime helper that marks the current cell as a ``ContentPageBlock``.

    Parameters
    ----------
    section : str | None
        Target document section (e.g. ``"middlematter"``). Routed
        through the same mechanism as :class:`NBPrintCell`.
    span : int | None
        Number of columns to span in a parent grid/columns layout.
    rows : int | None
        Number of rows to span in a grid layout.
    area : str | None
        Named grid area (paired with ``ContentPageBox.grid_template``).
    aspect : float | str | None
        Aspect-ratio constraint. Accepts ``1.7777``, ``"16:9"``, or a
        raw CSS value like ``"16/9"``.
    min_height, max_height : str | None
        CSS sizing constraints (e.g. ``"4in"``).
    break_inside : {"avoid", "auto"}
        ``"avoid"`` (default): keep the block on one page.
        ``"auto"``: allow it to flow across pages.
    scalable : bool | None
        Hint for the page-box ``fit`` pass: ``True`` to mark this
        block's content as scalable, ``False`` to opt out, ``None``
        (default) to auto-detect at render from child MIME types.
    css : str | None
        Extra CSS to merge into the block.
    style : Style | None
        Structured ``Style`` object merged into the block's style.
    classname : str | list[str] | None
        Extra CSS class(es) for the block wrapper.
    attrs : dict[str, str] | None
        Extra HTML attributes for the block wrapper.
    ignore : bool | None
        If ``True``, hide the block from the final output.
    emit : bool
        If ``True`` (default) immediately publish the metadata via
        ``display()``. Set to ``False`` when you only want to use the
        object as a context manager; metadata is emitted on
        ``__enter__``.

    """

    def __init__(
        self,
        *,
        section: str | None = None,
        span: int | None = None,
        rows: int | None = None,
        area: str | None = None,
        aspect: float | str | None = None,
        min_height: str | None = None,
        max_height: str | None = None,
        break_inside: BreakInside = "avoid",
        scalable: bool | None = None,
        css: str | None = None,
        style: Style | None = None,
        classname: str | list[str] | None = None,
        attrs: dict[str, str] | None = None,
        ignore: bool | None = None,
        emit: bool = True,
    ) -> None:
        self.section = section
        self.span = span
        self.rows = rows
        self.area = area
        self.aspect = aspect
        self.min_height = min_height
        self.max_height = max_height
        self.break_inside = break_inside
        self.scalable = scalable
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
        :class:`ContentPageBlock` rather than a plain :class:`Content`.
        """
        d: dict[str, Any] = {
            "type_": _PAGE_BLOCK_TYPE,
            "break_inside": self.break_inside,
        }
        if self.section is not None:
            d["section"] = self.section
        if self.span is not None:
            d["span"] = self.span
        if self.rows is not None:
            d["rows"] = self.rows
        if self.area is not None:
            d["area"] = self.area
        if self.aspect is not None:
            d["aspect"] = self.aspect
        if self.min_height is not None:
            d["min_height"] = self.min_height
        if self.max_height is not None:
            d["max_height"] = self.max_height
        if self.scalable is not None:
            d["scalable"] = self.scalable
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
        data = {NBPRINT_BLOCK_MIME: json.dumps(self.to_dict())}
        display(data, raw=True)
        self._emitted = True

    def __enter__(self) -> Self:
        if not self._emitted:
            self._emit()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return None
