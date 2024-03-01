from nbformat import NotebookNode
from pydantic import Field, PrivateAttr
from typing import TYPE_CHECKING, List

from .base import BaseModel

if TYPE_CHECKING:
    from .config import Configuration


class Context(BaseModel):
    tags: List[str] = Field(default=["nbprint:context"])
    role: str = "context"
    ignore: bool = True

    # internals
    _nb_var_name: str = PrivateAttr(default="nbprint_ctx")
    _context_generated: bool = PrivateAttr(default=False)

    class Config:
        arbitrary_types_allowed: bool = True
        extra: str = "allow"
        validate_assignment: bool = False

    def generate(
        self, metadata: dict, config: "Configuration", parent: BaseModel, attr: str = "", *args, **kwargs
    ) -> NotebookNode:
        self._context_generated = True
        return super().generate(metadata=metadata, config=config, parent=parent, attr=attr, *args, **kwargs)
