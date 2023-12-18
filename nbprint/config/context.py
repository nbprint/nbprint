from typing import TYPE_CHECKING, Optional

from nbformat import NotebookNode
from pydantic import PrivateAttr

from .base import BaseModel

if TYPE_CHECKING:
    from .config import Configuration


class Context(BaseModel):
    # internals
    _nb_var_name: str = PrivateAttr(default="nbprint_ctx")

    class Config:
        arbitrary_types_allowed: bool = True
        extra: str = "allow"
        validate_assignment: bool = False

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional["BaseModel"] = None,
    ) -> NotebookNode:
        cell = self._base_generate(metadata=metadata)
        cell.metadata.tags.append("nbprint:context")
        cell.metadata.nbprint.role = "context"
        cell.metadata.nbprint.ignore = True
        return cell
