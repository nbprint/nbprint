from enum import StrEnum
from pydantic_extra_types.color import Color
from typing import Literal, Optional

from .css import _BaseCss

__all__ = (
    "Color",  # reexport
    "Unset",
    "Direction",
)

Unset = Literal["unset"]


class Direction(StrEnum):
    left = "left"
    right = "right"
    top = "top"
    bottom = "bottom"


class _DirectionalSize(_BaseCss):
    right: Optional[int] = None
    left: Optional[int] = None
    top: Optional[int] = None
    bottom: Optional[int] = None
