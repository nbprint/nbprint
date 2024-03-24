from typing import Optional

from .common import _DirectionalSize
from .css import _BaseCss

__all__ = (
    "Padding",
    "Margin",
    "Spacing",
)


class Padding(_DirectionalSize): ...


class Margin(_DirectionalSize): ...


class Spacing(_BaseCss):
    padding: Optional[Padding]
    margin: Optional[Margin]
