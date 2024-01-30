from nbformat import NotebookNode
from pydantic import validator
from typing import TYPE_CHECKING, List, Optional, Union

from ..base import BaseModel
from ..utils import SerializeAsAny, _append_or_extend
from .common import LayoutHorizontalAlignment, LayoutJustify, LayoutVerticalAlignment
from .page_number import LayoutPageNumber

if TYPE_CHECKING:
    from ..config import Configuration


class Layout(BaseModel):
    vertical_alignment: Optional[SerializeAsAny[LayoutVerticalAlignment]] = None
    horizontal_alignment: Optional[SerializeAsAny[LayoutHorizontalAlignment]] = None
    justify: Optional[SerializeAsAny[LayoutJustify]] = None


class LayoutRegionBase(Layout):
    page_number: Optional[SerializeAsAny[LayoutPageNumber]] = None

    def _generate_helper(
        self,
        attr,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
    ) -> NotebookNode:
        cell = super()._base_generate(metadata=metadata, config=config, parent=parent, attr=attr)
        cell.metadata.tags.extend(["nbprint:layout", f"nbprint:layout:{attr}"])
        cell.metadata.nbprint.role = "layout"
        cell.metadata.nbprint.ignore = True

        return cell


class LayoutHeader(LayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("header", metadata=metadata, config=config, parent=parent)


class LayoutFooter(LayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("footer", metadata=metadata, config=config, parent=parent)


class LayoutLeft(LayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("left", metadata=metadata, config=config, parent=parent)


class LayoutRight(LayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("right", metadata=metadata, config=config, parent=parent)


class LayoutTopLeft(LayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("top_left", metadata=metadata, config=config, parent=parent)


class LayoutTopRight(LayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("top_right", metadata=metadata, config=config, parent=parent)


class LayoutBottomLeft(LayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("bottom_left", metadata=metadata, config=config, parent=parent)


class LayoutBottomRight(LayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("bottom_right", metadata=metadata, config=config, parent=parent)


class LayoutGlobal(BaseModel):
    header: Optional[SerializeAsAny[LayoutHeader]] = None
    footer: Optional[SerializeAsAny[LayoutFooter]] = None
    left: Optional[SerializeAsAny[LayoutLeft]] = None
    right: Optional[SerializeAsAny[LayoutRight]] = None
    top_left: Optional[SerializeAsAny[LayoutTopLeft]] = None
    top_right: Optional[SerializeAsAny[LayoutTopRight]] = None
    bottom_left: Optional[SerializeAsAny[LayoutBottomLeft]] = None
    bottom_right: Optional[SerializeAsAny[LayoutBottomRight]] = None

    @validator("header", pre=True)
    def convert_header_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutHeader)

    @validator("footer", pre=True)
    def convert_footer_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutFooter)

    @validator("left", pre=True)
    def convert_left_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutLeft)

    @validator("right", pre=True)
    def convert_right_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutRight)

    @validator("top_left", pre=True)
    def convert_top_left_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutTopLeft)

    @validator("top_right", pre=True)
    def convert_top_right_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutTopRight)

    @validator("bottom_left", pre=True)
    def convert_bottom_left_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutBottomLeft)

    @validator("bottom_right", pre=True)
    def convert_bottom_right_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutBottomRight)

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
    ) -> Optional[Union[NotebookNode, List[NotebookNode]]]:
        cells = []

        # parent and config should be equal for the global layout
        assert parent == config

        main_cell = super()._base_generate(metadata=metadata, config=config, parent=config, attr="layout")
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
                _append_or_extend(cells, getattr(self, attr).generate(metadata=metadata, config=config, parent=self))
        return cells
