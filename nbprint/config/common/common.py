from typing import Literal, Optional

from pydantic_extra_types.color import Color
from strenum import StrEnum

from .css import _BaseCss

__all__ = (
    "Color",  # reexport
    "Direction",
    "Element",
    "PseudoClass",
    "PseudoElement",
    "Unset",
)

Unset = Literal["unset"]

# class Size:
# cm Centimeters 1cm = 37.8px = 25.2/64in
# mm Millimeters 1mm = 1/10th of 1cm
# Q Quarter-millimeters 1Q = 1/40th of 1cm
# in Inches 1in = 2.54cm = 96px
# pc Picas 1pc = 1/6th of 1in
# pt Points 1pt = 1/72nd of 1in
# px Pixels 1px = 1/96th of 1in
# em Font size of the parent, in the case of typographical properties like font-size, and font size of the element itself,
#     in the case of other properties like width.
# ex x-height of the element's font.
# ch The advance measure (width) of the glyph "0" of the element's font.
# rem Font size of the root element.
# lh Line height of the element.
# rlh Line height of the root element. When used on the font-size or line-height properties of the root element, it refers
#     to the properties' initial value.
# vw 1% of the viewport's width.
# vh 1% of the viewport's height.
# vmin 1% of the viewport's smaller dimension.
# vmax 1% of the viewport's larger dimension.
# vb 1% of the size of the initial containing block in the direction of the root element's block axis.
# vi 1% of the size of the initial containing block in the direction of the root element's inline axis.
# svw, svh 1% of the small viewport's width and height, respectively.
# lvw, lvh 1% of the large viewport's width and height, respectively.
# dvw, dvh 1% of the dynamic viewport's width and height, respectively.


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


class PseudoClass(StrEnum):
    active = "active"
    checked = "checked"
    disabled = "disabled"
    empty = "empty"
    enabled = "enabled"
    first_child = "first-child"
    # :first-of-type
    focus = "focus"
    hover = "hover"
    # :in-range
    # :invalid
    # :lang(language) p:lang(it) Selects every <p> element with a lang attribute value starting with "it"
    last_child = "last-child"
    # :last-of-type
    # :link
    # :not(selector) :not(p) Selects every element that is not a <p> element
    # :nth-child(n) p:nth-child(2) Selects every <p> element that is the second child of its parent
    # :nth-last-child(n) p:nth-last-child(2) Selects every <p> element that is the second child of its parent, counting from the last child
    # :nth-last-of-type(n) p:nth-last-of-type(2) Selects every <p> element that is the second <p> element of its parent, counting from the last child
    # :nth-of-type(n) p:nth-of-type(2) Selects every <p> element that is the second <p> element of its parent
    # :only-of-type
    # :only-child
    # :optional
    # :out-of-range
    # :read-only
    # :read-write
    # :required
    # :root
    # :target
    # :valid
    visited = "visited"


class PseudoElement(StrEnum):
    after = "after"
    # backdrop = "backdrop"
    before = "before"
    # cue = "cue"
    # cue_region = "cue-region"
    first_letter = "first-letter"
    first_line = "first-line"
    # file_selector_button = "file-selector-button"
    # grammar_error = "grammar-error"
    marker = "marker"
    # part = "part(..."
    placeholder = "placeholder"
    selection = "selection"
    # slotted = "slotted(..."
    # spelling_error = "spelling-error"
    # target_text = "target-text"


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
