from __future__ import annotations

from strenum import StrEnum

from .css import _BaseCss

__all__ = (
    "FlexDirection",
    "VerticalAlignment",
    "HorizontalAlignment",
    "Justify",
    "DisplayKind",
    "FlexOptions",
    "Display",
)


class FlexDirection(StrEnum):
    row = "row"
    column = "column"


class VerticalAlignment(StrEnum):
    top = "top"
    center = "center"
    bottom = "bottom"


class HorizontalAlignment(StrEnum):
    left = "left"
    center = "center"
    right = "right"


class Justify(StrEnum):
    normal = "normal"
    center = "center"
    start = "start"
    end = "end"
    left = "left"
    right = "right"
    space_between = "space-between"
    space_around = "space-around"
    space_evenly = "space-evenly"


class DisplayKind(StrEnum):
    none = "none"
    flex = "flex"


class FlexOptions(_BaseCss):
    flex_direction: FlexDirection | None
    justify: Justify | None


class Display(_BaseCss):
    display: DisplayKind | None
    flex_options: FlexOptions | None
