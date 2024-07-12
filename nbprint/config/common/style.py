from __future__ import annotations

from pydantic import model_validator

from nbprint.config.base import BaseModel

from .border import Border
from .common import Element, PseudoClass, PseudoElement
from .spacing import Spacing
from .text import Font


class Scope(BaseModel):
    """Class to represent a css scope selection."""

    element: Element | str | None = ""

    id: str | None = ""
    classname: str | None = ""

    selector: str | None = ""

    pseudoclass: PseudoClass | None = ""
    pseudoelement: PseudoElement | None = ""

    @model_validator(mode="after")
    def check_any_set(self) -> Scope:
        """Helper method to test if any css rules are set, to determin if return should be empty string."""
        if all(element in ("", None) for element in (self.element, self.classname, self.id, self.selector)):
            msg = "Must set one of {element, classname, id, selector}"
            raise ValueError(msg)
        return self

    def __str__(self) -> str:
        """Convert scoping rules to css string."""
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
    """Class to represent a generic css style block."""

    scope: Scope | None = None
    spacing: Spacing | None = None
    font: Font | None = None
    border: Border | None = None

    def __str__(self) -> str:
        """Convert style rules to css string."""
        ret = f"{self.scope} {{\n"
        for part in (self.spacing, self.font, self.border):
            if part:
                part_str = str(part)
                if part_str:
                    ret += f"{part_str}\n"
        ret += "\n}"
        return ret.replace("\n\n", "\n").strip()
