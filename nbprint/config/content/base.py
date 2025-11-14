from typing import TYPE_CHECKING, Optional

from IPython.display import HTML
from nbformat import NotebookNode
from pydantic import Field, SerializeAsAny, field_validator

from nbprint.config.base import BaseModel, Role, _append_or_extend
from nbprint.config.common import Style
from nbprint.config.exceptions import NBPrintNullCellError

if TYPE_CHECKING:
    from nbprint.config.core import Configuration


class Content(BaseModel):
    content: str | list[SerializeAsAny[BaseModel]] | None = ""
    tags: list[str] = Field(default=["nbprint:content"])
    role: Role = Role.CONTENT

    # cell magics
    magics: list[str] | None = Field(default_factory=list, description="List of cell magics to apply to the cell")

    # used by lots of things
    style: Style | None = None

    def generate(
        self,
        metadata: dict | None = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
        attr: str = "",
        counter: int | None = None,
    ) -> NotebookNode | list[NotebookNode] | None:
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
                raise NBPrintNullCellError

        # prefix cells with magics
        for cell in cells:
            cell: NotebookNode
            if self.magics:
                for magic in self.magics:
                    cell.source = f"%%{magic}\n{cell.source}"
        return cells

    @field_validator("content", mode="before")
    @classmethod
    def convert_content_from_obj(cls, v) -> "Content":
        if v is None:
            return []
        if isinstance(v, list):
            for i, element in enumerate(v):
                if isinstance(element, str):
                    v[i] = Content(type_=element)
                elif isinstance(element, dict):
                    v[i] = BaseModel._to_type(element)
        return v

    def __call__(self, **_) -> HTML:
        return HTML("")


class ContentMarkdown(Content):
    content: str | None = ""

    def generate(
        self,
        metadata: dict | None = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
        **_,
    ) -> NotebookNode | list[NotebookNode] | None:
        cell = super()._base_generate_md(metadata=metadata, config=config, parent=parent)
        cell.source = self.content
        return cell


class ContentCode(Content): ...
