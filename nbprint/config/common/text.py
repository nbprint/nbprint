from enum import Enum

from ..base import BaseModel


class FontWeight(str, Enum):
    normal = "normal"
    bold = "bold"


class FontStyle(str, Enum):
    normal = "normal"
    italic = "italic"


class TextDecoration(str, Enum):
    none = "none"
    underline = "underline"


class Text(BaseModel):
    text: str = ""
    decoration: TextDecoration = TextDecoration.none
    style: FontStyle = FontStyle.normal
    weight: FontWeight = FontWeight.normal
