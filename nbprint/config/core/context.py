from typing import TYPE_CHECKING

from nbformat import NotebookNode
from pydantic import ConfigDict, Field, PrivateAttr, field_validator

from nbprint.config.base import BaseModel, Role

from .parameters import Parameters

if TYPE_CHECKING:
    from .config import Configuration

__all__ = ("Context",)


class Context(BaseModel):
    tags: list[str] = Field(default_factory=list)
    role: Role = Role.CONTEXT
    ignore: bool = True
    parameters: Parameters | None = None

    # internals
    _nb_var_name: str = PrivateAttr(default="nbprint_ctx")
    _context_generated: bool = PrivateAttr(default=False)

    model_config = ConfigDict(
        validate_assignment=False,
        extra="allow",
        arbitrary_types_allowed=True,
    )

    @field_validator("tags", mode="after")
    @classmethod
    def _ensure_tags(cls, v: list[str]) -> list[str]:
        if "nbprint:context" not in v:
            v.append("nbprint:context")
        return v

    def generate(self, metadata: dict, config: "Configuration", parent: BaseModel, attr: str = "", **kwargs) -> NotebookNode:
        self._context_generated = True
        # TODO: may need to attach parameters manually at some point
        # in the future once papermill integration is complete
        return super().generate(metadata=metadata, config=config, parent=parent, attr=attr, **kwargs)
