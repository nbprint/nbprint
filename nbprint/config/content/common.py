from IPython.display import Markdown
from pydantic import Field
from typing import List, Optional

from ..common import FontStyle, FontWeight, HorizontalAlignment, TextDecoration, VerticalAlignment
from ..utils import SerializeAsAny
from .base import Content


class TextComponent(Content):
    text: Optional[str] = ""
    horizontal_alignment: Optional[SerializeAsAny[HorizontalAlignment]] = None
    vertical_alignment: Optional[SerializeAsAny[VerticalAlignment]] = None
    font_weight: Optional[SerializeAsAny[FontWeight]] = None
    font_style: Optional[SerializeAsAny[FontStyle]] = None
    text_decoration: Optional[SerializeAsAny[TextDecoration]] = None

    tags: List[str] = Field(default=["nbprint:content"])

    def __call__(self, ctx=None, *args, **kwargs):
        return Markdown(self.text)
