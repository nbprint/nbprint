from pydantic import Field

from .base import Content


class ContentCover(Content):
    """Class to represent a cover page."""

    tags: list[str] = Field(default=["nbprint:content", "nbprint:content:cover"])
