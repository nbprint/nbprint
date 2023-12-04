import ast
from importlib import import_module
from json import dumps, loads
from typing import TYPE_CHECKING, List, Optional, Type, Union

from nbformat import NotebookNode
from nbformat.v4 import new_code_cell, new_markdown_cell
from pydantic import BaseModel, validator

from .utils import SerializeAsAny

if TYPE_CHECKING:
    from ..config import NBCXConfiguration
    from .context import NBCXContext


class NBCXType(BaseModel):
    module: str
    name: str

    @classmethod
    def from_string(cls, str: str) -> "NBCXType":
        module, name = str.split(":")
        return NBCXType(module=module, name=name)

    def to_string(self) -> str:
        return f"{self.module}:{self.name}"

    def type(self) -> Type["NBCXType"]:
        return getattr(import_module(self.module), self.name)

    def load(self, **kwargs) -> "NBCXType":
        return self.type()(**kwargs)


class NBCXBaseModel(BaseModel):
    type: SerializeAsAny[NBCXType]

    # internals
    _nb_var_name: Optional[str] = ""

    class Config:
        arbitrary_types_allowed: bool = False
        extra: str = "ignore"
        validate_assignment: bool = True

    def __init__(self, **kwargs):
        if "type" not in kwargs:
            kwargs["type"] = NBCXType(module=self.__class__.__module__, name=self.__class__.__name__)
        super().__init__(**kwargs)

    @validator("type", pre=True)
    def convert_type_string_to_module_and_name(cls, v):
        if isinstance(v, str):
            return NBCXType.from_string(v)
        return v

    @property
    def nb_var_name(self):
        if self._nb_var_name:
            return self._nb_var_name
        name = self.__class__.__name__.lower()
        if name.startswith("nbcx"):
            return name.replace("nbcx", "nbcx_")
        return f"nbcx_{name}"

    @staticmethod
    def _to_type(value, model_type=None):
        if value is None:
            value = {}

        if model_type is None and "type" in value:
            # derive type from instantiation
            model_type = NBCXBaseModel

        if isinstance(value, dict):
            return model_type(**value).type.load(**value)

        return value

    @classmethod
    def from_json(cls, json):
        data = loads(json)
        return cls(**data)

    def __call__(self, ctx: "NBCXContext" = None, *args, **kwargs) -> None:
        """Execute this model inside of a notebook

        Args:
            ctx (_type_, optional): _description_. Defaults to None.
        """
        ...

    def generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
        *args,
        **kwargs,
    ) -> Optional[Union[NotebookNode, List[NotebookNode]]]:
        """Generate a notebook node for this model.
        This will be called before the runtime of the notebook, use it for code generation.

        Args:
            metadata (dict): common cell metadata

        Returns:
            NotebookNode: the content of the notebook node
        """
        ...

    def _base_generate_meta(self, metadata: dict = None) -> Optional[NotebookNode]:
        cell = new_code_cell(metadata=metadata)
        cell.metadata.tags.extend(["nbcx"])
        cell.metadata.nbcx.role = "undefined"
        cell.metadata.nbcx.type = self.type.to_string()
        cell.metadata.nbcx.data = self.json()
        return cell

    def _base_generate_md_meta(self, metadata: dict = None) -> Optional[NotebookNode]:
        cell = new_markdown_cell(metadata=metadata)
        cell.metadata.tags.extend(["nbcx"])
        cell.metadata.nbcx.role = "undefined"
        cell.metadata.nbcx.type = self.type.to_string()
        return cell

    def _base_generate(
        self,
        metadata: Optional[dict] = None,
        config: Optional["NBCXConfiguration"] = None,
        parent: Optional["NBCXBaseModel"] = None,
        attr: str = "",
        counter: Optional[int] = None,
        call_with_context: str = "",
    ) -> Optional[NotebookNode]:
        cell = self._base_generate_meta(metadata=metadata)
        mod = ast.Module(body=[], type_ignores=[])

        if parent:
            value = ast.Attribute(value=ast.Name(id=parent.nb_var_name, ctx=ast.Load()), attr=attr, ctx=ast.Load())

            if counter is not None:
                value = ast.Subscript(
                    value=value,
                    slice=ast.Constant(value=counter),
                )
            mod.body.append(
                ast.Assign(
                    targets=[ast.Name(id=self.nb_var_name, ctx=ast.Store())],
                    value=value,
                    lineno=1,
                )
            )
        else:
            data = self.json()
            mod.body.append(
                ast.ImportFrom(
                    module=self.type.module,
                    names=[ast.alias(name=self.type.name)],
                    level=0,
                )
            )

            mod.body.append(
                ast.Assign(
                    targets=[ast.Name(id=self.nb_var_name, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=self.type.name, ctx=ast.Load()), attr="from_json", ctx=ast.Load()
                        ),
                        args=[ast.parse(dumps(data), mode="eval").body],
                        keywords=[],
                    ),
                    lineno=2,
                )
            )

        if call_with_context:
            mod.body.append(
                ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id=self.nb_var_name, ctx=ast.Load()),
                        args=[],
                        keywords=[ast.keyword(arg="ctx", value=ast.Name(id=call_with_context, ctx=ast.Load()))],
                    )
                )
            )
        else:
            mod.body.append(ast.Expr(value=ast.Name(id=self.nb_var_name, ctx=ast.Load())))

        source = ast.unparse(mod).replace('"', '\\"')
        cell.source = source
        return cell

    def _base_generate_md(
        self,
        metadata: Optional[dict] = None,
    ) -> Optional[NotebookNode]:
        cell = self._base_generate_md_meta(metadata=metadata)
        return cell

    def __repr__(self) -> str:
        # Truncate the output for now
        return f"<{self.__class__.__name__}>"
