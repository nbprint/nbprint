"""Runtime API for annotating notebook cells with nbprint metadata.

``NBPrintCell`` is designed to be used *inside* notebook cells at execution
time.  It emits a hidden ``display()`` output using a custom MIME type so
that the metadata survives in the cell's output list and can be picked up
by ``_cell_to_content`` during notebook ingestion.

Usage::

    from nbprint import NBPrintCell, Style, Font

    # Simple: mark this cell as covermatter with extra CSS
    NBPrintCell(section="covermatter", css=":scope { text-align: center; }")

    # Context manager: wrap outputs in a styled <div>
    with NBPrintCell(style=Style(font=Font(size=24))):
        display(Markdown("# Cover Page"))
"""

from __future__ import annotations

import json
from typing import Any

from IPython.display import display
from typing_extensions import Self

from nbprint.config.common import Style

__all__ = ("NBPRINT_MIME", "NBPrintCell")

NBPRINT_MIME = "application/nbprint.cell+json"


class NBPrintCell:
    """Runtime helper that emits nbprint cell metadata as a display output.

    Parameters
    ----------
    section : str | None
        Target document section (e.g. ``"covermatter"``, ``"frontmatter"``).
    css : str | None
        Raw CSS to merge into the cell.
    style : Style | None
        Structured ``Style`` object whose properties are converted to CSS.
    classname : str | list[str] | None
        Extra CSS class(es) to add to the cell wrapper.
    attrs : dict[str, str] | None
        Extra HTML attributes for the cell wrapper.
    ignore : bool | None
        If ``True``, hide the cell in the final output.
    emit : bool
        If ``True`` (default), immediately call ``display()`` with the
        metadata.  Set to ``False`` when used only as a context manager
        (metadata is emitted on ``__enter__``).

    """

    def __init__(
        self,
        *,
        section: str | None = None,
        css: str | None = None,
        style: Style | None = None,
        classname: str | list[str] | None = None,
        attrs: dict[str, str] | None = None,
        ignore: bool | None = None,
        emit: bool = True,
    ) -> None:
        self.section = section
        self.css = css
        self.style = style
        self.classname = classname
        self.attrs = attrs
        self.ignore = ignore
        self._emitted = False

        if emit:
            self._emit()

    # -- serialisation --------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict of non-None fields."""
        d: dict[str, Any] = {}
        if self.section is not None:
            d["section"] = self.section
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

    # -- display --------------------------------------------------------------

    def _emit(self) -> None:
        """Publish metadata via IPython ``display()``."""
        if self._emitted:
            return
        data = {NBPRINT_MIME: json.dumps(self.to_dict())}
        display(data, raw=True)
        self._emitted = True

    # -- context manager ------------------------------------------------------

    def __enter__(self) -> Self:
        if not self._emitted:
            self._emit()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return None
