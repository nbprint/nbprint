import ast
from json import dumps
from typing import TYPE_CHECKING

from nbformat import NotebookNode

from .base import NBCXBaseModel

if TYPE_CHECKING:
    from .config import NBCXConfiguration


class NBCXParameters(NBCXBaseModel):
    def generate(self, metadata: dict = None, config: "NBCXConfiguration" = None) -> NotebookNode:
        cell = self._base_generate_meta(metadata=metadata)
        cell.metadata.tags.extend(["parameters", "nbcx:parameters"])
        cell.metadata.nbcx.role = "parameters"
        cell.metadata.nbcx.ignore = True

        mod = ast.Module(body=[], type_ignores=[])
        for i, (k, v) in enumerate(self.dict().items()):
            if k in ("type",):
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
