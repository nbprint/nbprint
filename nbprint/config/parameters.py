import ast
from json import dumps
from nbformat import NotebookNode
from pydantic import Field
from typing import TYPE_CHECKING, List

from .base import BaseModel

if TYPE_CHECKING:
    from .config import Configuration


class Parameters(BaseModel):
    tags: List[str] = Field(default=["parameters", "nbprint:parameters"])
    role: str = "parameters"
    ignore: bool = True

    def generate(self, metadata: dict, config: "Configuration", *args, **kwargs) -> NotebookNode:
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
