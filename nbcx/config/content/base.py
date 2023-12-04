from typing import TYPE_CHECKING, List, Optional, Union

from nbformat import NotebookNode
from pydantic import validator

from ..base import NBCXBaseModel, NBCXType
from ..layout import NBCXLayout
from ..utils import SerializeAsAny

if TYPE_CHECKING:
    from ..config import NBCXConfiguration


class NBCXContent(NBCXBaseModel):
    content: Optional[Union[str, List[SerializeAsAny[NBCXBaseModel]]]] = ""
    layout: Optional[SerializeAsAny[NBCXLayout]] = None

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
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
            cell.metadata.tags.append("nbcx:content")
            cell.metadata.nbcx.role = "content"
            cell.metadata.nbcx.data = ""
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
                    v[i] = NBCXContent(type=NBCXType.from_string(element))
                elif isinstance(element, dict):
                    v[i] = NBCXBaseModel._to_type(element)
        return v


class NBCXContentMarkdown(NBCXContent):
    content: Optional[str] = ""

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
        attr: str = "",
        counter: Optional[int] = None,
    ) -> Optional[Union[NotebookNode, List[NotebookNode]]]:
        cell = super()._base_generate_md(metadata=metadata)
        cell.metadata.tags.append("nbcx:content")
        cell.metadata.nbcx.role = "content"
        cell.source = self.content
        return cell


class NBCXContentCode(NBCXContent):
    ...


class NBCXContentDynamic(NBCXContent):
    content: Optional[str] = ""

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
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
        cell.metadata.tags.extend(["nbcx:content", "nbcx:content:dynamic"])
        cell.metadata.nbcx.role = "content"
        return cell
