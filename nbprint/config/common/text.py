from __future__ import annotations

from strenum import StrEnum

from .common import Color
from .css import _BaseCss


class FontWeight(StrEnum):
    """Enumeration for `font-weight` css attribute."""

    normal = "normal"
    bold = "bold"


class FontStyle(StrEnum):
    """Enumeration for `font-style` css attribute."""

    normal = "normal"
    italic = "italic"


class TextDecoration(StrEnum):
    """Enumeration for `text-decoration` css attribute."""

    none = "none"
    underline = "underline"
    overline = "overline"
    dotted = "dotted"
    wavy = "wavy"


class TextTransform(StrEnum):
    """Enumeration for `text-transform` css attribute."""

    capitalize = "capitalize"
    lowercase = "lowercase"
    uppercase = "uppercase"


class FontFamily(StrEnum):
    """Enumeration for `font-family` css attribute."""

    serif = "serif"
    sans_serif = "sans-serif"
    monospace = "monospace"


class Font(_BaseCss):
    """Class to represent text formatting attributes, mapped to one or more css rules."""

    family: FontFamily | str | None = None
    size: int | None = None
    transform: TextTransform | None = None

    # TODO: multiple decorations and color decorations
    # text-decoration-color
    # text-decoration-line
    # text-decoration-style
    # text-decoration-thickness

    decoration: TextDecoration | None = None

    style: FontStyle | None = None
    weight: FontWeight | None = None
    color: Color | None = None

    def __str__(self) -> str:
        """Convert font rules to css rules."""
        ret = ""
        if self.family:
            ret += f"font-family: {self.family};\n"
        if self.size:
            ret += f"font-size: {self.size}px;\n"
        if self.transform:
            ret += f"text-transform: {self.transform};\n"
        if self.decoration:
            ret += f"text-decoration: {self.decoration};\n"
        if self.style:
            ret += f"font-style: {self.style};\n"
        if self.weight:
            ret += f"font-weight: {self.weight};\n"
        if self.color:
            ret += f"color: {self.color};\n"
        return ret.strip()


class Text(Font):
    """Class to represent text formatting attributes, mapped to one or more css rules."""
