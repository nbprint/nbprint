from typing import TYPE_CHECKING, Optional, Tuple, Union

from nbformat import NotebookNode
from pydantic import Field, field_validator

from .base import BaseModel, Role, _append_or_extend
from .common import PageOrientation, PageSize, Style
from .exceptions import NBPrintNullCellError

if TYPE_CHECKING:
    from .core.config import Configuration

__all__ = (
    "Page",
    "PageNumber",
    "PageRegion",
    "PageRegionContent",
)


class PageRegionContent(BaseModel):
    content: Optional[str] = ""

    # common
    tags: list[str] = Field(default=["nbprint:page"])
    role: Role = Role.PAGE
    ignore: bool = True

    def __str__(self) -> str:
        if self.content:
            return f"content: {self.content};"
        return ""


class PageNumber(PageRegionContent):
    content: Optional[str] = "counter(page)"


class PageRegion(BaseModel):
    _region: str = ""
    content: Optional[PageRegionContent] = Field(default_factory=PageNumber)
    style: Optional[Style] = None

    css: str = ""

    # common
    tags: list[str] = Field(default=["nbprint:page"])
    role: Role = Role.PAGE
    ignore: bool = True

    def generate(self, metadata: dict, config: "Configuration", parent: "BaseModel", attr: str, **_) -> NotebookNode:
        cell = super().generate(metadata=metadata, config=config, parent=parent, attr=attr)
        cell.metadata.tags.append(f"nbprint:page:{attr}")
        return cell


class Page(BaseModel):
    top: Optional[PageRegion] = None
    top_left: Optional[PageRegion] = None
    top_right: Optional[PageRegion] = None
    bottom: Optional[PageRegion] = None
    bottom_left: Optional[PageRegion] = None
    bottom_right: Optional[PageRegion] = None
    left: Optional[PageRegion] = None
    left_top: Optional[PageRegion] = None
    left_bottom: Optional[PageRegion] = None
    right: Optional[PageRegion] = None
    right_top: Optional[PageRegion] = None
    right_bottom: Optional[PageRegion] = None

    size: Optional[Union[PageSize, Tuple[float, float]]] = Field(default=PageSize.letter)
    orientation: Optional[PageOrientation] = Field(default=PageOrientation.portrait)

    pages: Optional[list["Page"]] = Field(default_factory=list)

    css: str = ""

    @classmethod
    def convert_region_from_obj(cls, v, region) -> PageRegion:
        ret = BaseModel._to_type(v, PageRegion)
        ret._region = region
        base_css_scope = "@page {{ @{region} {{ {content} }} }}".format(region=region, content=str(ret.content or ""))
        ret.css += base_css_scope
        return ret

    @field_validator("top", mode="before")
    @classmethod
    def convert_top_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "top-center")

    @field_validator("top_left", mode="before")
    @classmethod
    def convert_top_left_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "top-left")

    @field_validator("top_right", mode="before")
    @classmethod
    def convert_top_right_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "top-right")

    @field_validator("bottom", mode="before")
    @classmethod
    def convert_bottom_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "bottom-center")

    @field_validator("bottom_left", mode="before")
    @classmethod
    def convert_bottom_left_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "bottom-left")

    @field_validator("bottom_right", mode="before")
    @classmethod
    def convert_bottom_right_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "bottom-right")

    @field_validator("left", mode="before")
    @classmethod
    def convert_left_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "left-center")

    @field_validator("left_top", mode="before")
    @classmethod
    def convert_left_top_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "left-top")

    @field_validator("left_bottom", mode="before")
    @classmethod
    def convert_left_bottom_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "left-bottom")

    @field_validator("right", mode="before")
    @classmethod
    def convert_right_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "right-center")

    @field_validator("right_top", mode="before")
    @classmethod
    def convert_right_top_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "right-top")

    @field_validator("right_bottom", mode="before")
    @classmethod
    def convert_right_bottom_from_obj(cls, v) -> PageRegion:
        return Page.convert_region_from_obj(v, "right-bottom")

    def render(self, **_) -> None:
        if "@page { size:" not in self.css:
            if isinstance(self.size, tuple):
                self.css = (
                    self.css
                    + f"""
    @page {{ size: {self.size[0]}in {self.size[1]}in; }}
                """
                )
            else:
                self.css = (
                    self.css
                    + f"""
    @page {{ size: {self.size.value} {self.orientation.value}; }}
                """
                )

    def generate(
        self, metadata: dict, config: "Configuration", parent: "BaseModel", attr: str = "page", **_
    ) -> Optional[Union[NotebookNode, list[NotebookNode]]]:
        cells = []

        # parent and config should be equal for the global page layout
        assert parent == config

        main_cell = super()._base_generate(metadata=metadata, config=config, parent=config, attr=attr or "page")
        main_cell.metadata.tags.append("nbprint:page")
        main_cell.metadata.nbprint.role = "page"
        main_cell.metadata.nbprint.ignore = True
        cells.append(main_cell)

        for set_attr in (
            "top",
            "top_left",
            "top_right",
            "bottom",
            "bottom_left",
            "bottom_right",
            "left",
            "left_top",
            "left_bottom",
            "right",
            "right_top",
            "right_bottom",
        ):
            if getattr(self, set_attr) is not None:
                # pass in `self` as `parent here`
                _append_or_extend(cells, getattr(self, set_attr).generate(metadata=metadata, config=config, parent=self, attr=set_attr))
        for i, cell in enumerate(self.pages):
            _append_or_extend(
                cells,
                cell.generate(metadata=metadata, config=config, parent=self, attr="pages", counter=i),
            )
        for cell in cells:
            if cell is None:
                raise NBPrintNullCellError
        return cells

    @field_validator("pages", mode="before")
    @classmethod
    def convert_pages_from_obj(cls, v) -> "Page":
        if v is None:
            return []
        if isinstance(v, list):
            for i, element in enumerate(v):
                if isinstance(element, str):
                    v[i] = Page(type_=element)
                elif isinstance(element, dict):
                    v[i] = BaseModel._to_type(element)
        return v
