from nbformat import NotebookNode
from pydantic import validator
from typing import TYPE_CHECKING, List, Optional, Union

from ..base import BaseModel
from ..utils import SerializeAsAny, _append_or_extend
from .base import Page
from .page_number import PageNumber

if TYPE_CHECKING:
    from ..config import Configuration


class PageRegionBase(Page):
    page_number: Optional[SerializeAsAny[PageNumber]] = None

    def generate(
        self, metadata: dict, config: "Configuration", parent: "BaseModel", attr: str, *args, **kwargs
    ) -> NotebookNode:
        cell = super().generate(metadata=metadata, config=config, parent=parent, attr=attr)
        cell.metadata.tags.append(f"nbprint:page:{attr}")
        return cell


class PageHeader(PageRegionBase): ...


class PageFooter(PageRegionBase): ...


class PageLeftMargin(PageRegionBase): ...


class PageRightMargin(PageRegionBase): ...


class PageTopLeftMargin(PageRegionBase): ...


class PageTopRightMargin(PageRegionBase): ...


class PageBottomLeftMargin(PageRegionBase): ...


class PageBottomRightMargin(PageRegionBase): ...


class PageGlobal(BaseModel):
    header: Optional[SerializeAsAny[PageHeader]] = None
    footer: Optional[SerializeAsAny[PageFooter]] = None
    left: Optional[SerializeAsAny[PageLeftMargin]] = None
    right: Optional[SerializeAsAny[PageRightMargin]] = None
    top_left: Optional[SerializeAsAny[PageTopLeftMargin]] = None
    top_right: Optional[SerializeAsAny[PageTopRightMargin]] = None
    bottom_left: Optional[SerializeAsAny[PageBottomLeftMargin]] = None
    bottom_right: Optional[SerializeAsAny[PageBottomRightMargin]] = None

    @validator("header", pre=True)
    def convert_header_from_obj(cls, v):
        return BaseModel._to_type(v, PageHeader)

    @validator("footer", pre=True)
    def convert_footer_from_obj(cls, v):
        return BaseModel._to_type(v, PageFooter)

    @validator("left", pre=True)
    def convert_left_from_obj(cls, v):
        return BaseModel._to_type(v, PageLeftMargin)

    @validator("right", pre=True)
    def convert_right_from_obj(cls, v):
        return BaseModel._to_type(v, PageRightMargin)

    @validator("top_left", pre=True)
    def convert_top_left_from_obj(cls, v):
        return BaseModel._to_type(v, PageTopLeftMargin)

    @validator("top_right", pre=True)
    def convert_top_right_from_obj(cls, v):
        return BaseModel._to_type(v, PageTopRightMargin)

    @validator("bottom_left", pre=True)
    def convert_bottom_left_from_obj(cls, v):
        return BaseModel._to_type(v, PageBottomLeftMargin)

    @validator("bottom_right", pre=True)
    def convert_bottom_right_from_obj(cls, v):
        return BaseModel._to_type(v, PageBottomRightMargin)

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
            "header",
            "footer",
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
