from typing import Optional

from ..base import BaseModel
from .common import TextComponent


class LayoutPageNumber(BaseModel):
    text: Optional[TextComponent] = None
