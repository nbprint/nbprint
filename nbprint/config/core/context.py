from nbformat import NotebookNode
from pydantic import Field, PrivateAttr
from typing import TYPE_CHECKING

from nbprint.config.base import BaseModel, Role

if TYPE_CHECKING:
    from .config import Configuration

__all__ = ("Context",)


class Context(BaseModel):
    """Class representing a notebook global context, defined as a global variable in the notebook."""

    tags: list[str] = Field(default=["nbprint:context"])
    role: Role = Role.CONTEXT
    ignore: bool = True

    # internals
    _nb_var_name: str = PrivateAttr(default="nbprint_ctx")
    _context_generated: bool = PrivateAttr(default=False)

    class Config:
        """Pydantic configuration for context class."""

        arbitrary_types_allowed: bool = True
        extra: str = "allow"
        validate_assignment: bool = False

    def generate(self, metadata: dict, config: "Configuration", parent: BaseModel, attr: str = "", *args, **kwargs) -> NotebookNode:
        """Generate notebook cells for context, should occur before any substantive cells."""
        self._context_generated = True
        return super().generate(*args, metadata=metadata, config=config, parent=parent, attr=attr, **kwargs)
