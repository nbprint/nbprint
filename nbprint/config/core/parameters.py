import ast
from json import dumps
from typing import Any, Dict

from ccflow import ContextBase
from nbformat import NotebookNode
from pydantic import Field, model_validator

from nbprint.config.base import BaseModel, Role

__all__ = ("PapermillParameters", "Parameters")


class Parameters(ContextBase, BaseModel):
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
        for i, (k, v) in enumerate(self.model_dump(mode="json", exclude={"type", "tags", "role", "ignore"}).items()):
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


class PapermillParameters(Parameters):
    """Papermill parameters function implicitly as a dict"""

    vars: Dict[str, Any] = Field(default_factory=dict)

    def generate(self, metadata: dict, **_) -> NotebookNode:
        cell = self._base_generate_meta(metadata=metadata)
        mod = ast.Module(body=[], type_ignores=[])

        # Create a dictionary assignment for parameters
        for i, (k, v) in enumerate(self.vars.items()):
            if isinstance(v, bool):
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

    @model_validator(mode="before")
    @classmethod
    def _model_before_validator(cls, data) -> dict:
        # Move all fields except those defined in Parameters to vars
        params_fields = set(cls.model_fields.keys()) | {"_target_"}
        vars_dict = {k: v for k, v in data.items() if k not in params_fields}
        for k in vars_dict:
            data.pop(k)
        if "vars" not in data:
            data["vars"] = {}
        data["vars"].update(vars_dict)
        return data

    # NOTE: this shouldve been possible via a wrap or before validator,
    # but alas i could not get it to work
    def __setattr__(self, name: str, value) -> None:
        if name in self.model_fields and name != "vars":
            super().__setattr__(name, value)
        elif name == "vars":
            self.vars.update(value)
        else:
            self.vars[name] = value
