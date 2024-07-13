from typing import List

from pydantic import Field

from .base import Content


class ContentCover(Content):
    tags: List[str] = Field(default=["nbprint:content", "nbprint:content:cover"])
