from strenum import StrEnum

from .css import _BaseCss

__all__ = (
    "Display",
    "DisplayKind",
    "FlexDirection",
    "FlexOptions",
    "HorizontalAlignment",
    "Justify",
    "VerticalAlignment",
)


class FlexDirection(StrEnum):
    row = "row"
    column = "column"


class VerticalAlignment(StrEnum):
    top = "top"
    center = "center"
    bottom = "bottom"


class HorizontalAlignment(StrEnum):
    left = "left"
    center = "center"
    right = "right"


class Justify(StrEnum):
    normal = "normal"
    center = "center"
    start = "start"
    end = "end"
    left = "left"
    right = "right"
    space_between = "space-between"
    space_around = "space-around"
    space_evenly = "space-evenly"


class DisplayKind(StrEnum):
    none = "none"
    flex = "flex"


class FlexOptions(_BaseCss):
    flex_direction: FlexDirection | None = None
    justify: Justify | None = None

    def __str__(self) -> str:
        parts = []
        if self.flex_direction:
            parts.append(f"flex-direction: {self.flex_direction};")
        if self.justify:
            parts.append(f"justify-content: {self.justify};")
        return "\n".join(parts)


class Display(_BaseCss):
    display: DisplayKind | None = None
    flex_options: FlexOptions | None = None

    def __str__(self) -> str:
        parts = []
        if self.display:
            parts.append(f"display: {self.display};")
        if self.flex_options:
            flex_str = str(self.flex_options)
            if flex_str:
                parts.append(flex_str)
        return "\n".join(parts)
