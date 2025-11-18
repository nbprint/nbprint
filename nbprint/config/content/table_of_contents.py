from IPython.display import HTML, display
from pydantic import Field, field_validator

from .base import Content


class ContentTableOfContents(Content):
    tags: list[str] = Field(default_factory=list)

    def __call__(self, **_) -> None:
        display(HTML('<div id="toc"></div>'))
        # display(HTML('<p class="pagebreak"></p>'))

    @field_validator("tags", mode="after")
    @classmethod
    def _ensure_tags(cls, v: list[str]) -> list[str]:
        if "nbprint:content:table-of-contents" not in v:
            v.append("nbprint:content:table-of-contents")
        return v
