from typing import Optional

from ..base import BaseModel
from .spacing import Spacing
from .text import Text


class Style(BaseModel):
    spacing: Optional[Spacing]
    text: Optional[Text]
