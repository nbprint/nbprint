from IPython.display import HTML, display
from pydantic import Field

from .base import Content


class ContentTableOfContents(Content):
    """Class to server as placeholder for JS-generated table of contents."""

    tags: list[str] = Field(default=["nbprint:content", "nbprint:content:table-of-contents"])

    def __call__(self, *_, **__) -> None:
        """Create HTML compatible table of contents div block.

        Note: requires custom JS code
        """
        display(HTML('<div id="toc"></div>'))
