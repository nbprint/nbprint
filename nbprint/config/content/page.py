from IPython.display import HTML
from typing import List, Optional

from .base import Content


class ContentColumnLayout(Content):
    # component to split into certain number of columns
    count: int = 1
    sizes: List[float] = [1.0]
    separator_size: Optional[str] = None
    separator_color: Optional[str] = None

    def __call__(self, ctx=None, *args, **kwargs):
        # return empty html just for placeholder
        return HTML("")
