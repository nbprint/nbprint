from nbformat import NotebookNode
from pydantic import validator
from typing import TYPE_CHECKING, List, Optional, Union

from ..base import BaseModel
from ..utils import SerializeAsAny, _append_or_extend
from .base import Layout
from .page_number import LayoutPageNumber

if TYPE_CHECKING:
    from ..config import Configuration


class LayoutRegionBase(Layout):
    page_number: Optional[SerializeAsAny[LayoutPageNumber]] = None

    def generate(
        self, metadata: dict, config: "Configuration", parent: "BaseModel", attr: str, *args, **kwargs
    ) -> NotebookNode:
        cell = super().generate(metadata=metadata, config=config, parent=parent, attr=attr)
        cell.metadata.tags.append(f"nbprint:layout:{attr}")
        return cell


class LayoutHeader(LayoutRegionBase): ...


class LayoutFooter(LayoutRegionBase): ...


class LayoutLeftMargin(LayoutRegionBase): ...


class LayoutRightMargin(LayoutRegionBase): ...


class LayoutTopLeftMargin(LayoutRegionBase): ...


class LayoutTopRightMargin(LayoutRegionBase): ...


class LayoutBottomLeftMargin(LayoutRegionBase): ...


class LayoutBottomRightMargin(LayoutRegionBase): ...


class LayoutGlobal(BaseModel):
    header: Optional[SerializeAsAny[LayoutHeader]] = None
    footer: Optional[SerializeAsAny[LayoutFooter]] = None
    left: Optional[SerializeAsAny[LayoutLeftMargin]] = None
    right: Optional[SerializeAsAny[LayoutRightMargin]] = None
    top_left: Optional[SerializeAsAny[LayoutTopLeftMargin]] = None
    top_right: Optional[SerializeAsAny[LayoutTopRightMargin]] = None
    bottom_left: Optional[SerializeAsAny[LayoutBottomLeftMargin]] = None
    bottom_right: Optional[SerializeAsAny[LayoutBottomRightMargin]] = None

    @validator("header", pre=True)
    def convert_header_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutHeader)

    @validator("footer", pre=True)
    def convert_footer_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutFooter)

    @validator("left", pre=True)
    def convert_left_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutLeftMargin)

    @validator("right", pre=True)
    def convert_right_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutRightMargin)

    @validator("top_left", pre=True)
    def convert_top_left_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutTopLeftMargin)

    @validator("top_right", pre=True)
    def convert_top_right_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutTopRightMargin)

    @validator("bottom_left", pre=True)
    def convert_bottom_left_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutBottomLeftMargin)

    @validator("bottom_right", pre=True)
    def convert_bottom_right_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutBottomRightMargin)

    def generate(
        self, metadata: dict, config: "Configuration", parent: "BaseModel", attr: str = "layout", *args, **kwargs
    ) -> Optional[Union[NotebookNode, List[NotebookNode]]]:
        cells = []

        # parent and config should be equal for the global layout
        assert parent == config

        main_cell = super()._base_generate(metadata=metadata, config=config, parent=config, attr=attr)
        main_cell.metadata.tags.append("nbprint:layout")
        main_cell.metadata.nbprint.role = "layout"
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
