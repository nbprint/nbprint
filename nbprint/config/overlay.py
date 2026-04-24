"""Formatting overlays — rules that address cells during notebook ingestion
and merge formatting into (or wrap) the ``Content`` objects created from
them.

Two overlay kinds are supported:

* :class:`Overlay` — matches individual cells and *merges* formatting fields
  (``css``, ``classname``, ``attrs``, ``style``, ``ignore``) into the
  matching ``Content``.

* :class:`LayoutOverlay` — matches a contiguous range of cells and *wraps*
  them in a flex layout container (``row`` / ``column`` / ``inline``).
"""

from __future__ import annotations

from typing import Iterable, Literal

from pydantic import Field

from nbprint.config.base import BaseModel
from nbprint.config.common import Style
from nbprint.config.core.content import SECTION_ORDER, Section

__all__ = ("CellMatcher", "LayoutOverlay", "Overlay")


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


def _merge_formatting(
    target,
    *,
    css: str | None,
    classname: str | list[str] | None,
    attrs: dict[str, str] | None,
    style: Style | None,
    ignore: bool | None,
) -> None:
    """Merge formatting overrides into a ``Content`` or layout instance.

    - ``css`` is appended (stacks with existing CSS)
    - ``classname`` is appended (stacks as list)
    - ``attrs`` is merged (overlay keys win on collision)
    - ``style`` is merged via ``Style.merge`` (overlay fields win)
    - ``ignore`` is set when provided
    """
    if css:
        existing = getattr(target, "css", "") or ""
        target.css = f"{existing}\n{css}" if existing else css

    if classname:
        overlay_parts = [classname] if isinstance(classname, str) else list(classname)
        existing_cn = getattr(target, "classname", None)
        if isinstance(existing_cn, list):
            target.classname = [*existing_cn, *overlay_parts]
        elif existing_cn:
            target.classname = [existing_cn, *overlay_parts]
        else:
            target.classname = classname

    if attrs:
        merged = dict(getattr(target, "attrs", None) or {})
        merged.update(attrs)
        target.attrs = merged

    if style is not None:
        existing_style = getattr(target, "style", None)
        if isinstance(existing_style, Style):
            target.style = existing_style.merge(style)
        else:
            target.style = style

    if ignore is not None:
        target.ignore = ignore


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
        """Merge overlay overrides into the given ``Content`` instance."""
        _merge_formatting(
            content,
            css=self.css,
            classname=self.classname,
            attrs=self.attrs,
            style=self.style,
            ignore=self.ignore,
        )


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


class LayoutOverlay(BaseModel):
    """Structural overlay that wraps a contiguous range of cells in a layout.

    Matching uses the same :class:`CellMatcher` rules as :class:`Overlay`.
    Contiguous runs of matched cells (consecutive notebook indices that land
    in the same target section) are replaced by a single
    ``ContentFlexRowLayout`` / ``ContentFlexColumnLayout`` /
    ``ContentInlineLayout`` whose children are the matched ``Content``
    objects.
    """

    match: CellMatcher = Field(default_factory=CellMatcher)
    # Inclusive notebook-index range; if set, cells must fall within it to
    # match (in addition to any constraints in ``match``).
    index_range: tuple[int, int] | None = None

    layout: Literal["row", "column", "inline"] = "row"
    sizes: list[float] | None = None

    # Formatting applied to the wrapper itself (not its children)
    css: str | None = None
    classname: str | list[str] | None = None
    attrs: dict[str, str] | None = None
    style: Style | None = None

    def matches_cell(self, cell, index: int, section: str | None) -> bool:
        if self.index_range is not None:
            lo, hi = self.index_range
            if not (lo <= index <= hi):
                return False
        return self.match.matches(cell=cell, index=index, section=section)

    def build_wrapper(self, children: Iterable) -> BaseModel:
        """Instantiate the layout container wrapping ``children``."""
        # Lazy import to avoid cycles with the content package.
        from nbprint.config.content.page import (
            ContentFlexColumnLayout,
            ContentFlexRowLayout,
            ContentInlineLayout,
        )

        kinds = {
            "row": ContentFlexRowLayout,
            "column": ContentFlexColumnLayout,
            "inline": ContentInlineLayout,
        }
        cls = kinds[self.layout]

        kwargs: dict = {"content": list(children)}
        if self.sizes is not None and self.layout != "inline":
            kwargs["sizes"] = self.sizes

        wrapper = cls(**kwargs)
        _merge_formatting(
            wrapper,
            css=self.css,
            classname=self.classname,
            attrs=self.attrs,
            style=self.style,
            ignore=None,
        )
        return wrapper


def apply_layout_overlays(
    layout_overlays: list[LayoutOverlay],
    cells,
    placements: list,
    content_marshall,
) -> None:
    """Apply layout-wrapping overlays to already-placed cells.

    ``placements[i]`` is either ``None`` (cell was not routed) or a tuple
    ``(section_name, content_instance)``.  For each layout overlay we find
    contiguous runs of matched cells (consecutive notebook indices within the
    same section), remove their ``Content`` objects from the section, and
    insert a wrapper layout container at the position of the first matched
    cell.  Subsequent layout overlays can still match cells that were not
    consumed by an earlier overlay.
    """
    if not layout_overlays:
        return

    for lo in layout_overlays:
        matched: list[int] = []
        for i, cell in enumerate(cells):
            placement = placements[i]
            if placement is None:
                continue
            section, content_instance = placement
            section_list = getattr(content_marshall, section)
            if not any(c is content_instance for c in section_list):
                continue
            if lo.matches_cell(cell, index=i, section=section):
                matched.append(i)

        if not matched:
            continue

        # Group into contiguous runs (consecutive notebook indices, same section)
        runs: list[list[int]] = []
        cur: list[int] = []
        for i in matched:
            section = placements[i][0]
            if cur and i == cur[-1] + 1 and placements[cur[-1]][0] == section:
                cur.append(i)
            else:
                if cur:
                    runs.append(cur)
                cur = [i]
        if cur:
            runs.append(cur)

        # Replace each run (reverse order preserves earlier positions).
        for run in reversed(runs):
            section = placements[run[0]][0]
            section_list = getattr(content_marshall, section)
            children = [placements[i][1] for i in run]
            child_ids = {id(c) for c in children}

            start = next(idx for idx, c in enumerate(section_list) if id(c) in child_ids)
            remaining = [c for c in section_list if id(c) not in child_ids]
            wrapper = lo.build_wrapper(children)
            remaining.insert(start, wrapper)
            setattr(content_marshall, section, remaining)

            for i in run:
                placements[i] = None


def validate_section(name: str | None) -> str | None:
    """Return ``name`` if it's a valid section, else ``None``."""
    if name is None:
        return None
    return name if name in SECTION_ORDER else None
