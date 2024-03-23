from pydantic import Field
from typing import List, Optional

from ..base import BaseModel
from ..common import HorizontalAlignment, Justify, VerticalAlignment
from ..utils import Role, SerializeAsAny


class Page(BaseModel):
    vertical_alignment: Optional[SerializeAsAny[VerticalAlignment]] = None
    horizontal_alignment: Optional[SerializeAsAny[HorizontalAlignment]] = None
    justify: Optional[SerializeAsAny[Justify]] = None
    border_size: Optional[int] = None
    border_color: Optional[str] = None

    # common
    tags: List[str] = Field(default=["nbprint:page"])
    role: Role = Role.PAGE
    ignore: bool = True
