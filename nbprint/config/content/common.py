from __future__ import annotations

from IPython.display import Markdown
from pydantic import Field

from nbprint.config.common import FontStyle, FontWeight, HorizontalAlignment, TextDecoration, VerticalAlignment

from .base import Content


class TextComponent(Content):
    text: str | None = ""
    horizontal_alignment: HorizontalAlignment | None = None
    vertical_alignment: VerticalAlignment | None = None
    font_weight: FontWeight | None = None
    font_style: FontStyle | None = None
    text_decoration: TextDecoration | None = None

    tags: list[str] = Field(default=["nbprint:content"])

    def __call__(self, *_, **__):
        return Markdown(self.text)
