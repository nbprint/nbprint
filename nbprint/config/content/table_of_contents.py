from typing import List

from IPython.display import HTML, display
from pydantic import Field

from .base import Content


class ContentTableOfContents(Content):
    tags: List[str] = Field(default=["nbprint:content", "nbprint:content:table-of-contents"])

    def __call__(self, ctx=None, *args, **kwargs):
        display(HTML('<div id="toc"></div>'))
        # display(HTML('<p class="pagebreak"></p>'))
