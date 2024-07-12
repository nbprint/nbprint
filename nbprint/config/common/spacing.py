from __future__ import annotations

from .common import _DirectionalSize
from .css import _BaseCss

__all__ = (
    "Padding",
    "Margin",
    "Spacing",
)


class Padding(_DirectionalSize):
    """Class to represent CSS padding spacing."""

    def __str__(self) -> str:
        """Convert padding rules to css string."""
        return "\n".join(
            f"padding-{direction}: {getattr(self, direction, '')}px;"
            for direction in ("right", "left", "top", "bottom")
            if getattr(self, direction, "")
        ).strip()


class Margin(_DirectionalSize):
    """Class to represent CSS margin spacing."""

    def __str__(self) -> str:
        """Convert margin rules to css string."""
        return "\n".join(
            f"margin-{direction}: {getattr(self, direction, '')}px;"
            for direction in ("right", "left", "top", "bottom")
            if getattr(self, direction, "")
        ).strip()


class Spacing(_BaseCss):
    """Class to represent CSS spacing."""

    padding: Padding | None = None
    margin: Margin | None = None

    def __str__(self) -> str:
        """Convert various spacing rules to css string."""
        ret = ""
        if self.padding:
            ret += f"{self.padding}\n"
        if self.margin:
            ret += f"{self.margin}\n"
        return ret.strip()
