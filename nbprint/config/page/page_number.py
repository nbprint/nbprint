from typing import Optional

from ..base import BaseModel
from ..common import Text

__all__ = ("PageNumber",)


class PageNumber(BaseModel):
    # TODO text
    text: Optional[Text] = None

    def __str__(self) -> str:
        return "content: counter(page);"
