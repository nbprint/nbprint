from enum import Enum
from typing import Optional

from ..base import NBCXBaseModel
from ..utils import SerializeAsAny


class NBCXLayoutHorizontalAlignment(str, Enum):
    left = "left"
    center = "center"
    right = "right"


class NBCXLayoutVerticalAlignment(str, Enum):
    top = "top"
    center = "center"
    bottom = "bottom"


class NBCXLayoutFontWeight(str, Enum):
    normal = "normal"
    bold = "bold"


class NBCXLayoutJustify(str, Enum):
    normal = "normal"
    center = "center"
    start = "start"
    end = "end"
    left = "left"
    right = "right"
    space_between = "space-between"
    space_around = "space-around"
    space_evenly = "space-evenly"


class NBCXLayoutFontStyle(str, Enum):
    normal = "normal"
    italic = "italic"


class NBCXLayoutTextDecoration(str, Enum):
    none = "none"
    underline = "underline"


class NBCXTextComponent(NBCXBaseModel):
    content: Optional[str] = ""
    horizontal_alignment: Optional[SerializeAsAny[NBCXLayoutHorizontalAlignment]] = None
    vertical_alignment: Optional[SerializeAsAny[NBCXLayoutVerticalAlignment]] = None
    font_weight: Optional[SerializeAsAny[NBCXLayoutFontWeight]] = None
    font_style: Optional[SerializeAsAny[NBCXLayoutFontStyle]] = None
    text_decoration: Optional[SerializeAsAny[NBCXLayoutTextDecoration]] = None
