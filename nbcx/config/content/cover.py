from typing import TYPE_CHECKING, Optional

from nbformat import NotebookNode

from ..base import NBCXBaseModel
from .base import NBCXContent

if TYPE_CHECKING:
    from ..config import NBCXConfiguration


class NBCXContentCover(NBCXContent):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional[NBCXBaseModel] = None,
        attr: str = "",
        counter: Optional[int] = None,
    ) -> NotebookNode:
        cell = super()._base_generate(
            metadata=metadata,
            config=config,
            parent=parent,
            attr=attr,
            counter=counter,
            call_with_context=config.context.nb_var_name,
        )
        # add tags and role
        cell.metadata.tags.extend(["nbcx:content", "nbcx:content:cover"])
        cell.metadata.nbcx.role = "content"
        return cell
