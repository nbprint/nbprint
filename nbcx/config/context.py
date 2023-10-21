from typing import TYPE_CHECKING, Optional

from nbformat import NotebookNode
from pydantic import PrivateAttr

from .base import NBCXBaseModel

if TYPE_CHECKING:
    from .config import NBCXConfiguration


class NBCXContext(NBCXBaseModel):
    # internals
    _nb_var_name: str = PrivateAttr(default="nbcx_ctx")

    class Config:
        arbitrary_types_allowed: bool = True
        extra: str = "allow"
        validate_assignment: bool = False

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
    ) -> NotebookNode:
        cell = self._base_generate(metadata=metadata)
        cell.metadata.tags.append("nbcx:context")
        cell.metadata.nbcx.role = "context"
        cell.metadata.nbcx.ignore = True
        return cell
