from enum import StrEnum
from pydantic_extra_types.color import Color
from typing import Literal, Optional

from .css import _BaseCss

__all__ = (
    "Color",  # reexport
    "Unset",
    "Element",
    "Direction",
)

Unset = Literal["unset"]


class Element(StrEnum):
    div = "div"
    span = "span"
    p = "p"
    h1 = "h1"
    h2 = "h2"
    h3 = "h3"
    h4 = "h4"
    h5 = "h5"
    h6 = "h6"


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
