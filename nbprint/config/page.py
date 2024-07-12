from __future__ import annotations

from nbformat import NotebookNode
from pydantic import Field, field_validator
from typing import TYPE_CHECKING

from .base import BaseModel, Role, Type, _append_or_extend
from .common import PageOrientation, PageSize, Style

if TYPE_CHECKING:
    from .core.config import Configuration

__all__ = (
    "Page",
    "PageNumber",
    "PageRegion",
    "PageRegionContent",
)


class PageRegionContent(BaseModel):
    """Class that represents the contents of a region of the page."""

    content: str | None = ""

    # common
    tags: list[str] = Field(default=["nbprint:page"])
    role: Role = Role.PAGE
    ignore: bool = True

    def __str__(self) -> str:
        """Convert page region content to pagesjs expected html content."""
        if self.content:
            return f"content: {self.content};"
        return ""


class PageNumber(PageRegionContent):
    """Class that represents a page number."""

    content: str | None = "counter(page)"


class PageRegion(BaseModel):
    """Class that represents a region of a page."""

    _region: str = ""
    content: PageRegionContent | None = Field(default_factory=PageNumber)
    style: Style | None = None

    css: str = ""

    # common
    tags: list[str] = Field(default=["nbprint:page"])
    role: Role = Role.PAGE
    ignore: bool = True

    def generate(self, metadata: dict, config: Configuration, parent: BaseModel, attr: str, *_, **__) -> NotebookNode:
        """Generate cell for PageRegion object."""
        cell = super().generate(metadata=metadata, config=config, parent=parent, attr=attr)
        cell.metadata.tags.append(f"nbprint:page:{attr}")
        return cell


class Page(BaseModel):
    """Class that represents a page layout."""

    top: PageRegion | None = None
    top_left: PageRegion | None = None
    top_right: PageRegion | None = None
    bottom: PageRegion | None = None
    bottom_left: PageRegion | None = None
    bottom_right: PageRegion | None = None
    left: PageRegion | None = None
    left_top: PageRegion | None = None
    left_bottom: PageRegion | None = None
    right: PageRegion | None = None
    right_top: PageRegion | None = None
    right_bottom: PageRegion | None = None

    size: PageSize | None = Field(default=PageSize.letter)
    orientation: PageOrientation | None = Field(default=PageOrientation.portrait)

    pages: list[Page] | None = Field(default_factory=list)

    css: str = ""

    @classmethod
    def convert_region_from_obj(cls: Page, v: dict, region) -> PageRegion:
        """Type convert region of page from object."""
        ret = BaseModel._to_type(v, PageRegion)  # noqa: SLF001
        ret._region = region  # noqa: SLF001
        base_css_scope = "@page {{ @{region} {{ {content} }} }}".format(region=region, content=str(ret.content or ""))
        ret.css += base_css_scope
        return ret

    @field_validator("top", mode="before")
    @classmethod
    def convert_top_from_obj(cls, v) -> BaseModel:
        """Type convert to object in top."""
        return Page.convert_region_from_obj(v, "top-center")

    @field_validator("top_left", mode="before")
    @classmethod
    def convert_top_left_from_obj(cls, v) -> BaseModel:
        """Type convert to object in top left."""
        return Page.convert_region_from_obj(v, "top-left")

    @field_validator("top_right", mode="before")
    @classmethod
    def convert_top_right_from_obj(cls, v) -> BaseModel:
        """Type convert to object in top right."""
        return Page.convert_region_from_obj(v, "top-right")

    @field_validator("bottom", mode="before")
    @classmethod
    def convert_bottom_from_obj(cls, v) -> BaseModel:
        """Type convert to object in bottom."""
        return Page.convert_region_from_obj(v, "bottom-center")

    @field_validator("bottom_left", mode="before")
    @classmethod
    def convert_bottom_left_from_obj(cls, v) -> BaseModel:
        """Type convert to object in bottom left."""
        return Page.convert_region_from_obj(v, "bottom-left")

    @field_validator("bottom_right", mode="before")
    @classmethod
    def convert_bottom_right_from_obj(cls, v) -> BaseModel:
        """Type convert to object in bottom right."""
        return Page.convert_region_from_obj(v, "bottom-right")

    @field_validator("left", mode="before")
    @classmethod
    def convert_left_from_obj(cls, v) -> BaseModel:
        """Type convert to object in left."""
        return Page.convert_region_from_obj(v, "left-center")

    @field_validator("left_top", mode="before")
    @classmethod
    def convert_left_top_from_obj(cls, v) -> BaseModel:
        """Type convert to object in left top."""
        return Page.convert_region_from_obj(v, "left-top")

    @field_validator("left_bottom", mode="before")
    @classmethod
    def convert_left_bottom_from_obj(cls, v) -> BaseModel:
        """Type convert to object in left bottom."""
        return Page.convert_region_from_obj(v, "left-bottom")

    @field_validator("right", mode="before")
    @classmethod
    def convert_right_from_obj(cls, v) -> BaseModel:
        """Type convert to object in right."""
        return Page.convert_region_from_obj(v, "right-center")

    @field_validator("right_top", mode="before")
    @classmethod
    def convert_right_top_from_obj(cls, v) -> BaseModel:
        """Type convert to object in right top."""
        return Page.convert_region_from_obj(v, "right-top")

    @field_validator("right_bottom", mode="before")
    @classmethod
    def convert_right_bottom_from_obj(cls, v) -> BaseModel:
        """Type convert to object in right bottom."""
        return Page.convert_region_from_obj(v, "right-bottom")

    def render(self, *_, **__) -> None:
        """Render object before calling __call__."""
        if "@page { size:" not in self.css:
            self.css = (
                self.css
                + f"""
@page {{ size: {self.size.value} {self.orientation.value}; }}
            """
            )

    def generate(
        self, metadata: dict, config: Configuration, parent: BaseModel, attr: str = "page", *_, **__
    ) -> NotebookNode | list[NotebookNode] | None:
        """Generate cells from configuration."""
        cells = []

        # parent and config should be equal for the global page layout
        assert parent == config  # noqa: S101

        main_cell = super()._base_generate(metadata=metadata, config=config, parent=config, attr=attr or "page")
        main_cell.metadata.tags.append("nbprint:page")
        main_cell.metadata.nbprint.role = "page"
        main_cell.metadata.nbprint.ignore = True
        cells.append(main_cell)

        for attr_to_set in (
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
            if getattr(self, attr_to_set) is not None:
                # pass in `self` as `parent here`
                _append_or_extend(cells, getattr(self, attr_to_set).generate(metadata=metadata, config=config, parent=self, attr=attr_to_set))
        for i, cell in enumerate(self.pages):
            _append_or_extend(
                cells,
                cell.generate(metadata=metadata, config=config, parent=self, attr="pages", counter=i),
            )
        for cell in cells:
            if cell is None:
                msg = "got null cell, investigate!"
                raise RuntimeError(msg)
        return cells

    @field_validator("pages", mode="before")
    @classmethod
    def convert_pages_from_obj(cls, v) -> list:
        """Convert to list of pages."""
        if v is None:
            return []
        if isinstance(v, list):
            for i, element in enumerate(v):
                if isinstance(element, str):
                    v[i] = Page(type=Type.from_string(element))
                elif isinstance(element, dict):
                    v[i] = BaseModel._to_type(element)  # noqa: SLF001
        return v
