from typing import Optional

from strenum import StrEnum

from .css import _BaseCss

__all__ = (
    "Display",
    "DisplayKind",
    "FlexDirection",
    "FlexOptions",
    "HorizontalAlignment",
    "Justify",
    "VerticalAlignment",
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
    flex_direction: Optional[FlexDirection]
    justify: Optional[Justify]


class Display(_BaseCss):
    display: Optional[DisplayKind]
    flex_options: Optional[FlexOptions]
