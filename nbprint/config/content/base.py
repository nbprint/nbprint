from IPython.display import HTML
from nbformat import NotebookNode
from pydantic import Field, field_validator
from typing import TYPE_CHECKING, List, Optional, Union

from ..base import BaseModel, Role, SerializeAsAny, Type, _append_or_extend
from ..common import Style

if TYPE_CHECKING:
    from ..core import Configuration


class Content(BaseModel):
    content: Optional[Union[str, List[SerializeAsAny[BaseModel]]]] = ""
    tags: List[str] = Field(default=["nbprint:content"])
    role: Role = Role.CONTENT

    # used by lots of things
    style: Optional[Style] = None

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
        attr: str = "",
        counter: Optional[int] = None,
    ) -> Optional[Union[NotebookNode, List[NotebookNode]]]:
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
                raise Exception("got null cell, investigate!")
        return cells

    @field_validator("content", mode="before")
    def convert_content_from_obj(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            for i, element in enumerate(v):
                if isinstance(element, str):
                    v[i] = Content(type=Type.from_string(element))
                elif isinstance(element, dict):
                    v[i] = BaseModel._to_type(element)
        return v

    def __call__(self, *args, **kwargs):
        return HTML("")


class ContentMarkdown(Content):
    content: Optional[str] = ""

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
        attr: str = "",
        counter: Optional[int] = None,
    ) -> Optional[Union[NotebookNode, List[NotebookNode]]]:
        cell = super()._base_generate_md(metadata=metadata, config=config, parent=parent)
        cell.source = self.content
        return cell


class ContentCode(Content): ...
