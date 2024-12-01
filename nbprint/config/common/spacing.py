from typing import Optional

from .common import _DirectionalSize
from .css import _BaseCss

__all__ = (
    "Margin",
    "Padding",
    "Spacing",
)


class Padding(_DirectionalSize):
    def __str__(self) -> str:
        return "\n".join(
            f"padding-{direction}: {getattr(self, direction, '')}px;"
            for direction in ("right", "left", "top", "bottom")
            if getattr(self, direction, "")
        ).strip()


class Margin(_DirectionalSize):
    def __str__(self) -> str:
        return "\n".join(
            f"margin-{direction}: {getattr(self, direction, '')}px;"
            for direction in ("right", "left", "top", "bottom")
            if getattr(self, direction, "")
        ).strip()


class Spacing(_BaseCss):
    padding: Optional[Padding] = None
    margin: Optional[Margin] = None

    def __str__(self) -> str:
        ret = ""
        if self.padding:
            ret += f"{self.padding}\n"
        if self.margin:
            ret += f"{self.margin}\n"
        return ret.strip()
