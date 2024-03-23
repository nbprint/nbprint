from nbformat import NotebookNode
from pydantic import Field, validator
from typing import TYPE_CHECKING, List, Optional, Union

from ..base import BaseModel, Type
from ..utils import Role, SerializeAsAny, _append_or_extend

if TYPE_CHECKING:
    from ..config import Configuration


class Content(BaseModel):
    content: Optional[Union[str, List[SerializeAsAny[BaseModel]]]] = ""
    tags: List[str] = Field(default=["nbprint:content"])
    role: Role = Role.CONTENT

    # used by lots of things
    color: str = ""

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

    @validator("content", pre=True)
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
        cell = super()._base_generate_md(metadata=metadata)
        cell.source = self.content
        return cell


class ContentCode(Content): ...
