from nbformat import NotebookNode
from pydantic import Field, computed_field, validator
from typing import TYPE_CHECKING, List, Optional, Union

from ..base import BaseModel, _append_or_extend
from .base import Page
from .page_number import PageNumber

if TYPE_CHECKING:
    from ..core.config import Configuration

__all__ = (
    "PageRegionBase",
    "PageTop",
    "PageBottom",
    "PageLeft",
    "PageRight",
    "PageTopLeft",
    "PageTopRight",
    "PageBottomLeft",
    "PageBottomRight",
    "PageGlobal",
)


class PageRegionBase(Page):
    page_number: Optional[PageNumber] = None
    _base_css: str = "@page {{ @{region} {{ {content} }} }}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.css = self._base_css.format(region=self._region, content=str(self.page_number or ""))

    def generate(
        self, metadata: dict, config: "Configuration", parent: "BaseModel", attr: str, *args, **kwargs
    ) -> NotebookNode:
        cell = super().generate(metadata=metadata, config=config, parent=parent, attr=attr)
        cell.metadata.tags.append(f"nbprint:page:{attr}")
        return cell


# TODO corners
# TODO @left-top {}
# TODO @left-bottom {}
# TODO @right-top {}
# TODO @right-bottom {}


class PageTop(PageRegionBase):
    _region = "top-center"


class PageBottom(PageRegionBase):
    _region = "bottom-center"


class PageLeft(PageRegionBase):
    _region = "left-middle"


class PageRight(PageRegionBase):
    _region = "right-middle"


class PageTopLeft(PageRegionBase):
    _region = "top-left"


class PageTopRight(PageRegionBase):
    _region = "top-right"


class PageBottomLeft(PageRegionBase):
    _region = "bottom-left"


class PageBottomRight(PageRegionBase):
    _region = "bottom-right"


def _make_default_page_number() -> PageBottomRight:
    return PageBottomRight(page_number=PageNumber())


class PageGlobal(BaseModel):
    top: Optional[PageTop] = None
    bottom: Optional[PageBottom] = None
    left: Optional[PageLeft] = None
    right: Optional[PageRight] = None
    top_left: Optional[PageTopLeft] = None
    top_right: Optional[PageTopRight] = None
    bottom_left: Optional[PageBottomLeft] = None
    bottom_right: Optional[PageBottomRight] = Field(default_factory=_make_default_page_number)

    css: str = """
@page { size: letter; }
"""

    @validator("top", pre=True)
    def convert_top_from_obj(cls, v):
        return BaseModel._to_type(v, PageTop)

    @validator("bottom", pre=True)
    def convert_bottom_from_obj(cls, v):
        return BaseModel._to_type(v, PageBottom)

    @validator("left", pre=True)
    def convert_left_from_obj(cls, v):
        return BaseModel._to_type(v, PageLeft)

    @validator("right", pre=True)
    def convert_right_from_obj(cls, v):
        return BaseModel._to_type(v, PageRight)

    @validator("top_left", pre=True)
    def convert_top_left_from_obj(cls, v):
        return BaseModel._to_type(v, PageTopLeft)

    @validator("top_right", pre=True)
    def convert_top_right_from_obj(cls, v):
        return BaseModel._to_type(v, PageTopRight)

    @validator("bottom_left", pre=True)
    def convert_bottom_left_from_obj(cls, v):
        return BaseModel._to_type(v, PageBottomLeft)

    @validator("bottom_right", pre=True)
    def convert_bottom_right_from_obj(cls, v):
        return BaseModel._to_type(v, PageBottomRight)

    def generate(
        self, metadata: dict, config: "Configuration", parent: "BaseModel", attr: str = "page", *args, **kwargs
    ) -> Optional[Union[NotebookNode, List[NotebookNode]]]:
        cells = []

        # parent and config should be equal for the global page layout
        assert parent == config

        main_cell = super()._base_generate(metadata=metadata, config=config, parent=config, attr=attr)
        main_cell.metadata.tags.append("nbprint:page")
        main_cell.metadata.nbprint.role = "page"
        main_cell.metadata.nbprint.ignore = True
        cells.append(main_cell)

        for attr in (
            "top",
            "bottom",
            "left",
            "right",
            "top_left",
            "top_right",
            "bottom_left",
            "bottom_right",
        ):
            if getattr(self, attr) is not None:
                # pass in `self` as `parent here`
                _append_or_extend(
                    cells, getattr(self, attr).generate(metadata=metadata, config=config, parent=self, attr=attr)
                )
        return cells
