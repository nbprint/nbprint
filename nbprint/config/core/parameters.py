import ast
from json import dumps

from nbformat import NotebookNode
from pydantic import Field

from nbprint.config.base import BaseModel, Role

__all__ = ("Parameters",)


class Parameters(BaseModel):
    tags: list[str] = Field(default=["parameters", "nbprint:parameters"])
    role: Role = Role.PARAMETERS
    ignore: bool = True

    def generate(self, metadata: dict, **_) -> NotebookNode:
        cell = self._base_generate_meta(metadata=metadata)
        # if nb_vars:
        #     # add parameter variable
        #     nb_vars.add(k)

        mod = ast.Module(body=[], type_ignores=[])

        # NOTE: use model_dump(mode="json") here to be compatible with
        # papermill-based json parameters
        for i, (k, v) in enumerate(self.model_dump(mode="json").items()):
            if k in ("type", "tags", "role", "ignore"):
                continue
            if isinstance(v, bool):
                # Handle separately
                to_write = str(v)
            else:
                to_write = dumps(v)
                if isinstance(to_write, str) and (": true," in to_write or ": false," in to_write):
                    to_write = to_write.replace(": true,", ": True,").replace(": false,", ": False,")
            mod.body.append(
                ast.Assign(
                    targets=[ast.Name(id=k, ctx=ast.Store())],
                    value=ast.parse(to_write, mode="eval").body,
                    lineno=i,
                )
            )
        source = ast.unparse(mod).replace('"', '\\"')
        cell.source = source
        return cell
