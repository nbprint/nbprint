from __future__ import annotations

from IPython.display import Markdown
from pydantic import Field

from nbprint.config.common import FontStyle, FontWeight, HorizontalAlignment, TextDecoration, VerticalAlignment

from .base import Content


class TextComponent(Content):
    """Class to represent a text element."""

    text: str = Field(defaul="")
    horizontal_alignment: HorizontalAlignment | None = None
    vertical_alignment: VerticalAlignment | None = None
    font_weight: FontWeight | None = None
    font_style: FontStyle | None = None
    text_decoration: TextDecoration | None = None

    tags: list[str] = Field(default=["nbprint:content"])

    def __call__(self, *_, **__) -> Markdown:
        """Generate IPython HTML for object."""
        return Markdown(self.text)
