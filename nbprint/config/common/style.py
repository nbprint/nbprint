from pydantic import model_validator

from nbprint.config.base import BaseModel
from nbprint.config.exceptions import NBPrintBadScopeError

from .border import Border
from .common import Element, PseudoClass, PseudoElement
from .spacing import Spacing
from .text import Font

__all__ = (
    "Scope",
    "Style",
)


class Scope(BaseModel):
    element: Element | str | None = ""

    id: str | None = ""
    classname: str | None = ""

    selector: str | None = ""

    pseudoclass: PseudoClass | None = ""
    pseudoelement: PseudoElement | None = ""

    @model_validator(mode="after")
    def check_any_set(self) -> "Scope":
        if all(element in ("", None) for element in (self.element, self.classname, self.id, self.selector)):
            raise NBPrintBadScopeError
        return self

    def __str__(self) -> str:
        ret = ""
        if self.element:
            ret = f"{self.element}"
        if self.id:
            ret = f"{ret}#{self.id}"
        if self.classname:
            ret = f"{ret}.{self.classname}"
        if self.selector:
            ret = f"{ret}[{self.selector}]"
        if self.pseudoclass:
            ret = f"{ret}:{self.pseudoclass}"
        if self.pseudoelement:
            ret = f"{ret}::{self.pseudoclass}"
        return ret


class Style(BaseModel):
    scope: Scope | None = None
    spacing: Spacing | None = None
    font: Font | None = None
    border: Border | None = None

    def to_css_properties(self) -> str:
        """Return just the CSS property declarations (no selector wrapping)."""
        parts = []
        for part in (self.spacing, self.font, self.border):
            if part:
                part_str = str(part)
                if part_str:
                    parts.append(part_str)
        return "\n".join(parts)

    def merge(self, other: "Style") -> "Style":
        """Return a new Style with fields from ``other`` overriding ``self``."""
        return Style(
            scope=other.scope if other.scope is not None else self.scope,
            spacing=other.spacing if other.spacing is not None else self.spacing,
            font=other.font if other.font is not None else self.font,
            border=other.border if other.border is not None else self.border,
        )

    def __str__(self) -> str:
        props = self.to_css_properties()
        if self.scope:
            ret = f"{self.scope} {{\n{props}\n}}"
            return ret.replace("\n\n", "\n").strip()
        return props
