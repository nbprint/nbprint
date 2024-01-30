from IPython.display import Image, display
from nbformat import NotebookNode
from pathlib import Path
from pydantic import FilePath, validator
from typing import TYPE_CHECKING, Optional

from ..base import BaseModel
from .base import Content

if TYPE_CHECKING:
    from ..config import Configuration


class ContentImage(Content):
    path: Optional[FilePath] = None
    content: Optional[bytes] = b""

    @validator("path", pre=True)
    def convert_path_from_obj(cls, v):
        if isinstance(v, str):
            v = Path(v).resolve()
        return v

    @validator("content", pre=True)
    def convert_content_from_obj(cls, v):
        if v is None:
            return b""
        if v and isinstance(v, str):
            v = Path(v).resolve()
        if v and isinstance(v, Path):
            v = v.read_bytes()
        return v

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional[BaseModel] = None,
        attr: str = "",
        counter: Optional[int] = None,
    ) -> NotebookNode:
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

    def __call__(self, ctx=None, *args, **kwargs):
        if self.path:
            display(Image(filename=self.path))
        else:
            display(Image(data=self.content))

    def __repr__(self) -> str:
        return f"Image(path='{self.path}', content=[{len(self.content)} bytes])"
