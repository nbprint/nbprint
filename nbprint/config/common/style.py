from typing import Optional, Union

from ..base import BaseModel
from .common import Element
from .spacing import Spacing
from .text import Text


class Scope(BaseModel):
    element: Optional[Union[Element, str]]
    classname: Optional[str]
    id: Optional[str]
    selector: Optional[str]


class Style(BaseModel):
    scope: Optional[Scope]
    spacing: Optional[Spacing]
    text: Optional[Text]
