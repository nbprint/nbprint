import ast
from json import dumps
from typing import TYPE_CHECKING

from nbformat import NotebookNode
from pydantic import Field

from ..base import BaseModel, Role

if TYPE_CHECKING:
    from .config import Configuration

__all__ = ("Parameters",)


class Parameters(BaseModel):
    tags: list[str] = Field(default=["parameters", "nbprint:parameters"])
    role: Role = Role.PARAMETERS
    ignore: bool = True

    def generate(self, metadata: dict, config: "Configuration", *_, **__) -> NotebookNode:
        cell = self._base_generate_meta(metadata=metadata)
        # if nb_vars:
        #     # add parameter variable
        #     nb_vars.add(k)

        mod = ast.Module(body=[], type_ignores=[])
        for i, (k, v) in enumerate(self.dict().items()):
            if k in ("type", "tags", "role", "ignore"):
                continue
            mod.body.append(
                ast.Assign(
                    targets=[ast.Name(id=k, ctx=ast.Store())],
                    value=ast.parse(dumps(v), mode="eval").body,
                    lineno=i,
                )
            )
        source = ast.unparse(mod).replace('"', '\\"')
        cell.source = source
        return cell
