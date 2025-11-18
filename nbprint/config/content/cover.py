from pydantic import Field, field_validator

from .base import Content


class ContentCover(Content):
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags", mode="after")
    @classmethod
    def _ensure_tags(cls, v: list[str]) -> list[str]:
        if "nbprint:content:cover" not in v:
            v.append("nbprint:content:cover")
        return v
