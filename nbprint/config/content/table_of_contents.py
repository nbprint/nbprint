from IPython.display import HTML, display
from pydantic import Field

from .base import Content


class ContentTableOfContents(Content):
    tags: list[str] = Field(default=["nbprint:content", "nbprint:content:table-of-contents"])

    def __call__(self, **_) -> None:
        display(HTML('<div id="toc"></div>'))
        # display(HTML('<p class="pagebreak"></p>'))
