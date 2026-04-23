"""Formatting overlays — cell-addressing rules that merge formatting into
``Content`` objects during notebook ingestion.

An overlay is a ``match`` spec plus override fields (css, classname, attrs,
style, ignore).  Any Content built from a cell whose raw cell matches the
``CellMatcher`` has the overlay's overrides merged in.

Example (YAML)::

    overlays:
      - match: {index: 0}
        css: ":scope { text-align: center; }"
      - match: {tag: "chart"}
        style:
          border: {bottom: {width: 2, style: solid, color: "#333"}}
      - match: {cell_type: markdown}
        classname: "prose-body"
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from nbprint.config.base import BaseModel
from nbprint.config.common import Style
from nbprint.config.core.content import SECTION_ORDER, Section

__all__ = ("CellMatcher", "Overlay")


class CellMatcher(BaseModel):
    """Criteria for selecting cells to apply an overlay to.

    All set fields must match (AND).  An empty matcher matches every cell.
    """

    index: int | None = None
    tag: str | None = None
    cell_type: Literal["code", "markdown"] | None = None
    section: Section | None = None

    def matches(self, cell, index: int, section: str | None) -> bool:
        if self.index is not None and self.index != index:
            return False
        if self.tag is not None:
            tags = cell.get("metadata", {}).get("tags", []) if hasattr(cell, "get") else []
            if self.tag not in tags:
                return False
        if self.cell_type is not None and self.cell_type != getattr(cell, "cell_type", None):
            return False
        return not (self.section is not None and self.section != (section or "middlematter"))


class Overlay(BaseModel):
    """Formatting overlay merged into matching cells' ``Content``."""

    match: CellMatcher = Field(default_factory=CellMatcher)

    # Override fields (all optional)
    css: str | None = None
    classname: str | list[str] | None = None
    attrs: dict[str, str] | None = None
    style: Style | None = None
    ignore: bool | None = None

    def apply(self, content) -> None:
        """Merge overlay overrides into the given ``Content`` instance.

        - ``css`` is appended (stacks with existing CSS)
        - ``classname`` is appended (stacks)
        - ``attrs`` is merged (overlay keys win)
        - ``style`` is merged via ``Style.merge`` (overlay fields win)
        - ``ignore`` is set if the overlay provides a value
        """
        if self.css:
            content.css = f"{content.css}\n{self.css}" if content.css else self.css

        if self.classname:
            overlay_parts = [self.classname] if isinstance(self.classname, str) else list(self.classname)
            existing = content.classname
            if isinstance(existing, list):
                content.classname = [*existing, *overlay_parts]
            elif existing:
                content.classname = [existing, *overlay_parts]
            else:
                content.classname = self.classname

        if self.attrs:
            merged = dict(content.attrs or {})
            merged.update(self.attrs)
            content.attrs = merged

        if self.style is not None:
            if isinstance(content.style, Style):
                content.style = content.style.merge(self.style)
            else:
                content.style = self.style

        if self.ignore is not None:
            content.ignore = self.ignore


def apply_overlays(overlays: list[Overlay], cell, content, index: int, section: str | None) -> None:
    """Apply all matching overlays from ``overlays`` to ``content``.

    Overlays are applied in list order; later overlays layer on top of earlier
    ones.
    """
    if not overlays:
        return
    for overlay in overlays:
        if overlay.match.matches(cell=cell, index=index, section=section):
            overlay.apply(content)


def validate_section(name: str | None) -> str | None:
    """Return ``name`` if it's a valid section, else ``None``."""
    if name is None:
        return None
    return name if name in SECTION_ORDER else None
