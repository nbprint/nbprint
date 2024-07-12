from IPython.display import HTML, display
from pydantic import Field

from .base import Content


class ContentPageBreak(Content):
    """Class to represent placeholder for pagedjs page-break directive."""

    tags: list[str] = Field(default=["nbprint:content", "nbprint:content:pagebreak"])

    def __call__(self, *_, **__) -> None:
        """Create HTML compatible table of contents div block.

        Note: requires custom CSS
        """
        display(HTML('<p class="pagebreak"></p>'))
