from IPython.display import HTML, display
from pydantic import Field

from .base import Content


class ContentPageBreak(Content):
    tags: list[str] = Field(default=["nbprint:content", "nbprint:content:pagebreak"])

    def __call__(self, **_) -> None:
        display(HTML('<p class="pagebreak"></p>'))
