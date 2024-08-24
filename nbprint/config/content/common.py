from typing import Optional

from IPython.display import Markdown
from pydantic import Field

from nbprint.config.common import FontStyle, FontWeight, HorizontalAlignment, TextDecoration, VerticalAlignment

from .base import Content


class TextComponent(Content):
    text: Optional[str] = ""
    horizontal_alignment: Optional[HorizontalAlignment] = None
    vertical_alignment: Optional[VerticalAlignment] = None
    font_weight: Optional[FontWeight] = None
    font_style: Optional[FontStyle] = None
    text_decoration: Optional[TextDecoration] = None

    tags: list[str] = Field(default=["nbprint:content"])

    def __call__(self, **_) -> Markdown:
        return Markdown(self.text)
