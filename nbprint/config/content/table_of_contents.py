from IPython.display import HTML, display
from nbformat import NotebookNode
from typing import TYPE_CHECKING, Optional

from ..base import BaseModel
from .base import Content

if TYPE_CHECKING:
    from ..config import Configuration


class ContentTableOfContents(Content):
    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["Configuration"] = None,
        parent: Optional[BaseModel] = None,
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
        cell.metadata.tags.extend(["nbprint:content", "nbprint:content:table-of-contents"])
        cell.metadata.nbprint.role = "content"
        return cell

    def __call__(self, ctx=None, *args, **kwargs):
        display(HTML('<div id="toc"></div>'))
        # display(HTML('<p class="pagebreak"></p>'))
