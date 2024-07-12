from __future__ import annotations

from strenum import StrEnum

from .common import Color
from .css import _BaseCss

__all__ = (
    "BorderLineStyle",
    "BorderLineWidth",
    "BorderStyle",
    "Border",
)


class BorderLineStyle(StrEnum):
    """Enumeration of possible `border-style` css options."""

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
    """Enumeration of possible `border-width` css options."""

    thin = "thin"
    medium = "medium"
    thick = "thick"


class BorderStyle(_BaseCss):
    """Class to contain various css options for border styling."""

    width: BorderLineWidth | int
    style: BorderLineStyle
    color: Color

    def __str__(self) -> str:
        """Convert various border style rules to css string."""
        return f"{self.width}px {self.style} {self.color}"


class Border(_BaseCss):
    """Class to contain various css options for borders."""

    right: BorderStyle | None = None
    left: BorderStyle | None = None
    top: BorderStyle | None = None
    bottom: BorderStyle | None = None

    def __str__(self) -> str:
        """Convert various border rules to css string."""
        return "\n".join(
            f"border-{direction}: {getattr(self, direction, '')};" for direction in ("right", "left", "top", "bottom") if getattr(self, direction, "")
        ).strip()
