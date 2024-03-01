from typing import Optional

from ..base import BaseModel
from ..common import Text


class LayoutPageNumber(BaseModel):
    text: Optional[Text] = None
