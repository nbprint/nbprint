from enum import StrEnum
from typing import Optional, Union

from .common import Color
from .css import _BaseCss

__all__ = (
    "BorderLineStyle",
    "BorderLineWidth",
    "Border",
)


class BorderLineStyle(StrEnum):
    none = "none"
    hidden = "hidden"
    dotted = "dotted"
    dashed = "dashed"
    solid = "solid"
    double = "double"
    groove = "groove"
    ridge = "ridge"
    inset = "inset"
    outset = "outset"


class BorderLineWidth(StrEnum):
    thin = "thin"
    medium = "medium"
    thick = "thick"


class Border(_BaseCss):
    width: Optional[Union[BorderLineWidth, int]]
    style: Optional[BorderLineStyle]
    color: Optional[Color]
