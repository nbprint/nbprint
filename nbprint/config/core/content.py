from pydantic import Field, PrivateAttr, model_validator

from nbprint.config.base import BaseModel
from nbprint.config.content import Content

__all__ = ("ContentMarshall",)


class ContentMarshall(BaseModel):
    prematter: list[Content] = Field(default_factory=list)
    frontmatter: list[Content] = Field(default_factory=list)
    middlematter: list[Content] = Field(default_factory=list)
    endmatter: list[Content] = Field(default_factory=list)

    _all: list[Content] = PrivateAttr(default_factory=list)

    @model_validator(mode="after")
    def _all(self) -> "ContentMarshall":
        self._all = self.prematter + self.frontmatter + self.middlematter + self.endmatter
        return self

    # override indexing to return from _all
    def __getitem__(self, index: int) -> Content:
        return self._all[index]

    @property
    def all(self) -> list[Content]:
        return self._all
