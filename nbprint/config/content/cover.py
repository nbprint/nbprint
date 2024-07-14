from pydantic import Field

from .base import Content


class ContentCover(Content):
    tags: list[str] = Field(default=["nbprint:content", "nbprint:content:cover"])
