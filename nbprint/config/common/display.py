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
    """Enumeration of possible `flex-direction` css options."""

    row = "row"
    column = "column"


class VerticalAlignment(StrEnum):
    """Enumeration of possible `align-*` css options."""

    top = "top"
    center = "center"
    bottom = "bottom"


class HorizontalAlignment(StrEnum):
    """Enumeration of possible `align-*` css options."""

    left = "left"
    center = "center"
    right = "right"


class Justify(StrEnum):
    """Enumeration of possible `justify-*` css options."""

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
    """Enumeration of possible `display` css options."""

    none = "none"
    flex = "flex"


class FlexOptions(_BaseCss):
    """Helper class to aggregate of css `flex` configuration."""

    flex_direction: FlexDirection | None
    justify: Justify | None


class Display(_BaseCss):
    """Helper class to aggregate of css `display` configuration."""

    display: DisplayKind | None
    flex_options: FlexOptions | None
