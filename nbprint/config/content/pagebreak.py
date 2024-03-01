from IPython.display import HTML, display
from pydantic import Field
from typing import List

from .base import Content


class ContentPageBreak(Content):
    tags: List[str] = Field(default=["nbprint:content", "nbprint:content:pagebreak"])

    def __call__(self, ctx=None, *args, **kwargs):
        display(HTML('<p class="pagebreak"></p>'))
