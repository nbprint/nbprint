from pathlib import Path
from typing import TYPE_CHECKING, Optional

from IPython.display import Image, display
from nbformat import NotebookNode
from pydantic import FilePath, validator

from ..base import NBCXBaseModel
from .base import NBCXContent

if TYPE_CHECKING:
    from ..config import NBCXConfiguration


class NBCXContentImage(NBCXContent):
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
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional[NBCXBaseModel] = None,
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
        cell.metadata.tags.extend(["nbcx:content", "nbcx:content:dynamic"])
        cell.metadata.nbcx.role = "content"
        return cell

    def __call__(self, ctx=None, *args, **kwargs):
        if self.path:
            display(Image(filename=self.path))
        else:
            display(Image(data=self.content))

    def __repr__(self) -> str:
        return f"NBCXImage(path='{self.path}', content=[{len(self.content)} bytes])"
