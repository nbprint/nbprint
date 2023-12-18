from enum import Enum
from typing import Optional

from ..base import BaseModel
from ..utils import SerializeAsAny


class LayoutHorizontalAlignment(str, Enum):
    left = "left"
    center = "center"
    right = "right"


class LayoutVerticalAlignment(str, Enum):
    top = "top"
    center = "center"
    bottom = "bottom"


class LayoutFontWeight(str, Enum):
    normal = "normal"
    bold = "bold"


class LayoutJustify(str, Enum):
    normal = "normal"
    center = "center"
    start = "start"
    end = "end"
    left = "left"
    right = "right"
    space_between = "space-between"
    space_around = "space-around"
    space_evenly = "space-evenly"


class LayoutFontStyle(str, Enum):
    normal = "normal"
    italic = "italic"


class LayoutTextDecoration(str, Enum):
    none = "none"
    underline = "underline"


class TextComponent(BaseModel):
    content: Optional[str] = ""
    horizontal_alignment: Optional[SerializeAsAny[LayoutHorizontalAlignment]] = None
    vertical_alignment: Optional[SerializeAsAny[LayoutVerticalAlignment]] = None
    font_weight: Optional[SerializeAsAny[LayoutFontWeight]] = None
    font_style: Optional[SerializeAsAny[LayoutFontStyle]] = None
    text_decoration: Optional[SerializeAsAny[LayoutTextDecoration]] = None
