from typing import Optional

from ..base import NBCXBaseModel
from .common import NBCXTextComponent


class NBCXLayoutPageNumber(NBCXBaseModel):
    text: Optional[NBCXTextComponent] = None
