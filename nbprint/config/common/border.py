from typing import Optional, Union

from strenum import StrEnum

from .common import Color
from .css import _BaseCss

__all__ = (
    "Border",
    "BorderLineStyle",
    "BorderLineWidth",
    "BorderStyle",
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


class BorderStyle(_BaseCss):
    width: Union[BorderLineWidth, int]
    style: BorderLineStyle
    color: Color

    def __str__(self) -> str:
        return f"{self.width}px {self.style} {self.color}"


class Border(_BaseCss):
    right: Optional[BorderStyle] = None
    left: Optional[BorderStyle] = None
    top: Optional[BorderStyle] = None
    bottom: Optional[BorderStyle] = None

    def __str__(self) -> str:
        return "\n".join(
            f"border-{direction}: {getattr(self, direction, '')};" for direction in ("right", "left", "top", "bottom") if getattr(self, direction, "")
        ).strip()
