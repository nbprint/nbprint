from typing import Optional

from ..base import BaseModel
from ..common import Text


class PageNumber(BaseModel):
    text: Optional[Text] = None
