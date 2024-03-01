from enum import Enum


class HorizontalAlignment(str, Enum):
    left = "left"
    center = "center"
    right = "right"


class VerticalAlignment(str, Enum):
    top = "top"
    center = "center"
    bottom = "bottom"


class Justify(str, Enum):
    normal = "normal"
    center = "center"
    start = "start"
    end = "end"
    left = "left"
    right = "right"
    space_between = "space-between"
    space_around = "space-around"
    space_evenly = "space-evenly"
