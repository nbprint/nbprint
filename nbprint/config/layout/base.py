from pydantic import Field
from typing import List, Optional

from ..base import BaseModel
from ..common import HorizontalAlignment, Justify, VerticalAlignment
from ..utils import SerializeAsAny


class Layout(BaseModel):
    vertical_alignment: Optional[SerializeAsAny[VerticalAlignment]] = None
    horizontal_alignment: Optional[SerializeAsAny[HorizontalAlignment]] = None
    justify: Optional[SerializeAsAny[Justify]] = None
    border_size: Optional[int] = None
    border_color: Optional[str] = None

    # common
    tags: List[str] = Field(default=["nbprint:layout"])
    role: str = "layout"
    ignore: bool = True
