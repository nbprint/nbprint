from typing import TYPE_CHECKING, List, Optional, Union

from nbformat import NotebookNode
from pydantic import validator

from ..base import NBCXBaseModel
from ..utils import SerializeAsAny, _append_or_extend
from .common import NBCXLayoutHorizontalAlignment, NBCXLayoutJustify, NBCXLayoutVerticalAlignment
from .page_number import NBCXLayoutPageNumber

if TYPE_CHECKING:
    from ..config import NBCXConfiguration


class NBCXLayout(NBCXBaseModel):
    vertical_alignment: Optional[SerializeAsAny[NBCXLayoutVerticalAlignment]] = None
    horizontal_alignment: Optional[SerializeAsAny[NBCXLayoutHorizontalAlignment]] = None
    justify: Optional[SerializeAsAny[NBCXLayoutJustify]] = None


class NBCXLayoutRegionBase(NBCXLayout):
    page_number: Optional[SerializeAsAny[NBCXLayoutPageNumber]] = None

    def _generate_helper(
        self,
        attr,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
    ) -> NotebookNode:
        cell = super()._base_generate(metadata=metadata, config=config, parent=parent, attr=attr)
        cell.metadata.tags.extend(["nbcx:layout", f"nbcx:layout:{attr}"])
        cell.metadata.nbcx.role = "layout"
        cell.metadata.nbcx.ignore = True

        return cell


class NBCXLayoutHeader(NBCXLayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("header", metadata=metadata, config=config, parent=parent)


class NBCXLayoutFooter(NBCXLayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("footer", metadata=metadata, config=config, parent=parent)


class NBCXLayoutLeft(NBCXLayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("left", metadata=metadata, config=config, parent=parent)


class NBCXLayoutRight(NBCXLayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("right", metadata=metadata, config=config, parent=parent)


class NBCXLayoutTopLeft(NBCXLayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("top_left", metadata=metadata, config=config, parent=parent)


class NBCXLayoutTopRight(NBCXLayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("top_right", metadata=metadata, config=config, parent=parent)


class NBCXLayoutBottomLeft(NBCXLayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("bottom_left", metadata=metadata, config=config, parent=parent)


class NBCXLayoutBottomRight(NBCXLayoutRegionBase):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
    ) -> NotebookNode:
        return self._generate_helper("bottom_right", metadata=metadata, config=config, parent=parent)


class NBCXLayoutGlobal(NBCXBaseModel):
    header: Optional[SerializeAsAny[NBCXLayoutHeader]] = None
    footer: Optional[SerializeAsAny[NBCXLayoutFooter]] = None
    left: Optional[SerializeAsAny[NBCXLayoutLeft]] = None
    right: Optional[SerializeAsAny[NBCXLayoutRight]] = None
    top_left: Optional[SerializeAsAny[NBCXLayoutTopLeft]] = None
    top_right: Optional[SerializeAsAny[NBCXLayoutTopRight]] = None
    bottom_left: Optional[SerializeAsAny[NBCXLayoutBottomLeft]] = None
    bottom_right: Optional[SerializeAsAny[NBCXLayoutBottomRight]] = None

    @validator("header", pre=True)
    def convert_header_from_obj(cls, v):
        return NBCXBaseModel._to_type(v, NBCXLayoutHeader)

    @validator("footer", pre=True)
    def convert_footer_from_obj(cls, v):
        return NBCXBaseModel._to_type(v, NBCXLayoutFooter)

    @validator("left", pre=True)
    def convert_left_from_obj(cls, v):
        return NBCXBaseModel._to_type(v, NBCXLayoutLeft)

    @validator("right", pre=True)
    def convert_right_from_obj(cls, v):
        return NBCXBaseModel._to_type(v, NBCXLayoutRight)

    @validator("top_left", pre=True)
    def convert_top_left_from_obj(cls, v):
        return NBCXBaseModel._to_type(v, NBCXLayoutTopLeft)

    @validator("top_right", pre=True)
    def convert_top_right_from_obj(cls, v):
        return NBCXBaseModel._to_type(v, NBCXLayoutTopRight)

    @validator("bottom_left", pre=True)
    def convert_bottom_left_from_obj(cls, v):
        return NBCXBaseModel._to_type(v, NBCXLayoutBottomLeft)

    @validator("bottom_right", pre=True)
    def convert_bottom_right_from_obj(cls, v):
        return NBCXBaseModel._to_type(v, NBCXLayoutBottomRight)

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
    ) -> Optional[Union[NotebookNode, List[NotebookNode]]]:
        cells = []

        # parent and config should be equal for the global layout
        assert parent == config

        main_cell = super()._base_generate(metadata=metadata, config=config, parent=config, attr="layout")
        main_cell.metadata.tags.append("nbcx:layout")
        main_cell.metadata.nbcx.role = "layout"
        main_cell.metadata.nbcx.ignore = True
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
