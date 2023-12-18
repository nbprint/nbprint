from typing import TYPE_CHECKING, List, Optional, Union

from nbformat import NotebookNode
from pydantic import validator

from ..base import BaseModel, Type
from ..layout import Layout
from ..utils import SerializeAsAny

if TYPE_CHECKING:
    from ..config import Configuration


class Content(BaseModel):
    content: Optional[Union[str, List[SerializeAsAny[BaseModel]]]] = ""
    layout: Optional[SerializeAsAny[Layout]] = None

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
        attr: str = "",
        counter: Optional[int] = None,
    ) -> Optional[Union[NotebookNode, List[NotebookNode]]]:
        if isinstance(self.content, list):
            cells = [
                c.generate(metadata=metadata, config=config, parent=self, attr="content", counter=i)
                for i, c in enumerate(self.content)
            ]
        else:
            cell = super()._base_generate(
                metadata=metadata, config=config, parent=parent, attr="content", counter=counter
            )
            cell.metadata.tags.append("nbprint:content")
            cell.metadata.nbprint.role = "content"
            cell.metadata.nbprint.data = ""
            cell.source = self.content
            cells = [cell]
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
        cell.metadata.tags.append("nbprint:content")
        cell.metadata.nbprint.role = "content"
        cell.source = self.content
        return cell


class ContentCode(Content):
    ...


class ContentDynamic(Content):
    content: Optional[str] = ""

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
        attr: str = "",
        counter: Optional[int] = None,
    ) -> Optional[Union[NotebookNode, List[NotebookNode]]]:
        # force parent to None to load from json explicitly
        cell = super()._base_generate(
            metadata=metadata,
            config=config,
            parent=parent,
            attr=attr,
            counter=counter,
            call_with_context=config.context.nb_var_name,
        )

        # add tags and role
        cell.metadata.tags.extend(["nbprint:content", "nbprint:content:dynamic"])
        cell.metadata.nbprint.role = "content"
        return cell
