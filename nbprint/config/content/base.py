from __future__ import annotations

from IPython.display import HTML
from nbformat import NotebookNode
from pydantic import Field, field_validator
from typing import TYPE_CHECKING

from nbprint.config.base import BaseModel, Role, SerializeAsAny, Type, _append_or_extend
from nbprint.config.common import Style
from nbprint.config.exceptions import NBPrintGenerationError

if TYPE_CHECKING:
    from nbprint.config.core import Configuration


class Content(BaseModel):
    """Class representing some notebook cell content."""

    content: str | list[SerializeAsAny[BaseModel]] = Field(default="")
    tags: list[str] = Field(default=["nbprint:content"])
    role: Role = Role.CONTENT

    # used by lots of things
    style: Style | None = None

    def generate(  # noqa: PLR0913
        self,
        metadata: dict | None = None,
        config: Configuration | None = None,
        parent: BaseModel | None = None,
        attr: str = "",
        counter: int | None = None,
    ) -> NotebookNode | list[NotebookNode] | None:
        """Generate notebook code cells for content."""
        # make a cell for yourself
        self_cell = super().generate(
            metadata=metadata,
            config=config,
            parent=parent,
            attr=attr or "content",
            counter=counter,
        )
        if isinstance(self.content, str) and self.content:
            # replace content if its a str
            self_cell.source = self.content

            # remove the data, redundant
            self_cell.metadata.nbprint.data = ""

        cells = [self_cell]

        if isinstance(self.content, list):
            for i, cell in enumerate(self.content):
                _append_or_extend(
                    cells,
                    cell.generate(metadata=metadata, config=config, parent=self, attr=attr or "content", counter=i),
                )
        for cell in cells:
            if cell is None:
                msg = "got null cell, investigate!"
                raise NBPrintGenerationError(msg)
        return cells

    @field_validator("content", mode="before")
    @classmethod
    def convert_content_from_obj(cls, v) -> BaseModel:
        """Helper method to create a content object from a dict."""
        if v is None:
            return []
        if isinstance(v, list):
            for i, element in enumerate(v):
                if isinstance(element, str):
                    v[i] = Content(type=Type.from_string(element))
                elif isinstance(element, dict):
                    v[i] = BaseModel._to_type(element)  # noqa: SLF001
        return v

    def __call__(self, *_, **__) -> HTML:
        """Generate IPython HTML for object."""
        return HTML("")


class ContentMarkdown(Content):
    """Class representing some notebook markdown cell content."""

    content: str = Field(default="")

    def generate(
        self,
        metadata: dict | None = None,
        config: Configuration | None = None,
        parent: BaseModel | None = None,
        *_,
        **__,
    ) -> NotebookNode | list[NotebookNode] | None:
        """Generate notebook markdown cells for content."""
        cell = super()._base_generate_md(metadata=metadata, config=config, parent=parent)
        cell.source = self.content
        return cell


class ContentCode(Content):
    """Class representing some notebook code cell content."""
