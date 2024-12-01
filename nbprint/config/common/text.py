from typing import Optional, Union

from strenum import StrEnum

from .common import Color
from .css import _BaseCss

__all__ = (
    "Font",
    "FontFamily",
    "FontStyle",
    "FontWeight",
    "Text",
    "TextDecoration",
    "TextTransform",
)


class FontWeight(StrEnum):
    normal = "normal"
    bold = "bold"


class FontStyle(StrEnum):
    normal = "normal"
    italic = "italic"


class TextDecoration(StrEnum):
    none = "none"
    underline = "underline"
    overline = "overline"
    dotted = "dotted"
    wavy = "wavy"


class TextTransform(StrEnum):
    capitalize = "capitalize"
    lowercase = "lowercase"
    uppercase = "uppercase"


class FontFamily(StrEnum):
    serif = "serif"
    sans_serif = "sans-serif"
    monospace = "monospace"


class Font(_BaseCss):
    family: Optional[Union[FontFamily, str]] = None
    size: Optional[int] = None
    transform: Optional[TextTransform] = None

    # TODO: multiple decorations and color decorations
    # text-decoration-color
    # text-decoration-line
    # text-decoration-style
    # text-decoration-thickness

    decoration: Optional[TextDecoration] = None

    style: Optional[FontStyle] = None
    weight: Optional[FontWeight] = None
    color: Optional[Color] = None

    def __str__(self) -> str:
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


class Text(Font): ...
