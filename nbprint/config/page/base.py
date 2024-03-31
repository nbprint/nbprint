from pydantic import Field
from typing import List, Optional

from ..base import BaseModel, Role
from ..common import HorizontalAlignment, Justify, VerticalAlignment

__all__ = ("Page",)


class Page(BaseModel):
    vertical_alignment: Optional[VerticalAlignment] = None
    horizontal_alignment: Optional[HorizontalAlignment] = None
    justify: Optional[Justify] = None
    border_size: Optional[int] = None
    border_color: Optional[str] = None

    # common
    tags: List[str] = Field(default=["nbprint:page"])
    role: Role = Role.PAGE
    ignore: bool = True
