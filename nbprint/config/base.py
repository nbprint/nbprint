import ast
from importlib import import_module
from IPython.display import DisplayObject
from json import dumps, loads
from nbformat import NotebookNode
from nbformat.v4 import new_code_cell, new_markdown_cell
from pathlib import Path
from pydantic import BaseModel, Field, PrivateAttr, validator
from typing import TYPE_CHECKING, List, Optional, Type, Union
from uuid import uuid4

# from .exceptions import NBPrintGenerationException
from .utils import SerializeAsAny

if TYPE_CHECKING:
    from ..config import Configuration
    from .context import Context


class Type(BaseModel):
    module: str
    name: str

    @classmethod
    def from_string(cls, str: str) -> "Type":
        module, name = str.split(":")
        return Type(module=module, name=name)

    def to_string(self) -> str:
        return f"{self.module}:{self.name}"

    def type(self) -> Type["Type"]:
        return getattr(import_module(self.module), self.name)

    def load(self, **kwargs) -> "Type":
        return self.type()(**kwargs)


class BaseModel(BaseModel):
    # type info
    type: SerializeAsAny[Type]

    # basic metadata
    tags: List[str] = Field(default_factory=list)
    role: str = "undefined"
    ignore: bool = False

    # frontend code
    # This is designed to match anywidget
    css: Optional[Union[str, Path]] = Field(default="")
    esm: Optional[Union[str, Path]] = Field(default="")

    # internals
    # Variable to use inside notebook for this model
    _nb_var_name: Optional[str] = PrivateAttr(default="")

    # id to use to reconstitute dom during page building
    _id: str = PrivateAttr(default_factory=lambda: str(uuid4()))

    class Config:
        arbitrary_types_allowed: bool = False
        extra: str = "ignore"
        validate_assignment: bool = True

    def __init__(self, **kwargs):
        if "type" not in kwargs:
            kwargs["type"] = Type(module=self.__class__.__module__, name=self.__class__.__name__)
        super().__init__(**kwargs)

    @validator("css", pre=True)
    def convert_css_string_or_path_to_string_or_path(cls, v):
        if isinstance(v, str):
            if v.strip().endswith(".css"):
                # TODO resolve relative to class?
                v = Path(v).resolve().read_text()
        return v

    @validator("esm", pre=True)
    def convert_esm_string_or_path_to_string_or_path(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.endswith(".js") or v.endswith(".mjs"):
                # TODO resolve relative to class?
                v = Path(v).resolve().read_text()
        return v

    @validator("type", pre=True)
    def convert_type_string_to_module_and_name(cls, v):
        if isinstance(v, str):
            return Type.from_string(v)
        return v

    @property
    def nb_var_name(self):
        if self._nb_var_name:
            return self._nb_var_name
        name = self.__class__.__name__.lower()
        if name.startswith("nbprint"):
            return name.replace("nbprint", "nbprint_")
        return f"nbprint_{name}"

    def _recalculate_nb_var_name(self, nb_vars: set):
        attempt = 0
        test_nb_var_name = self.nb_var_name
        while test_nb_var_name in nb_vars:
            test_nb_var_name = f"{self.nb_var_name}{attempt}"
            attempt += 1
        # reset var name
        self._nb_var_name = test_nb_var_name
        # put in set
        nb_vars.add(self._nb_var_name)

    @staticmethod
    def _to_type(value, model_type=None):
        if value is None:
            value = {}

        if model_type is None and "type" in value:
            # derive type from instantiation
            model_type = BaseModel

        if isinstance(value, dict):
            return model_type(**value).type.load(**value)

        return value

    @classmethod
    def from_json(cls, json):
        data = loads(json)
        return cls(**data)

    def __call__(self, ctx: "Context" = None, *args, **kwargs) -> Optional[DisplayObject]:
        """Execute this model inside of a notebook

        Args:
            ctx (_type_, optional): _description_. Defaults to None.
        """
        return self

    def generate(
        self,
        metadata: dict,
        config: Optional["Configuration"],
        parent: Optional["BaseModel"] = None,
        attr: str = "",
        counter: Optional[int] = None,
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
        return self._base_generate(metadata=metadata, config=config, parent=parent, attr=attr, counter=counter)

    def _base_generate_meta(self, metadata: dict = None) -> Optional[NotebookNode]:
        cell = new_code_cell(metadata=metadata)
        cell.metadata.tags = list(set(["nbprint"] + (self.tags or [])))
        cell.metadata.nbprint.id = self._id
        cell.metadata.nbprint.role = self.role or "undefined"
        cell.metadata.nbprint.type = self.type.to_string()
        cell.metadata.nbprint.data = self.json()
        cell.metadata.nbprint.ignore = self.ignore or False
        return cell

    def _base_generate_md_meta(self, metadata: dict = None) -> Optional[NotebookNode]:
        cell = new_markdown_cell(metadata=metadata)
        cell.metadata.tags = list(set(["nbprint"] + (self.tags or [])))
        cell.metadata.nbprint.id = self._id
        cell.metadata.nbprint.role = self.role or "undefined"
        cell.metadata.nbprint.type = self.type.to_string()
        cell.metadata.nbprint.ignore = self.ignore or False
        return cell

    def _base_generate(
        self,
        metadata: dict,
        config: "Configuration",
        parent: Optional["BaseModel"] = None,
        attr: str = "",
        counter: Optional[int] = None,
    ) -> Optional[NotebookNode]:
        cell = self._base_generate_meta(metadata=metadata)
        mod = ast.Module(body=[], type_ignores=[])

        assert config is not None
        self._recalculate_nb_var_name(config._nb_vars)

        if parent and attr:
            # set in metadata
            if parent.ignore is False:
                cell.metadata.nbprint["parent-id"] = parent._id

            # now construct accessor
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

        if config and config.context and config.context._context_generated:
            call_with_context = config.context.nb_var_name
        else:
            call_with_context = "None"

        mod.body.append(
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id=self.nb_var_name, ctx=ast.Load()),
                    args=[],
                    keywords=[ast.keyword(arg="ctx", value=ast.Name(id=call_with_context, ctx=ast.Load()))],
                )
            )
        )
        # this line just puts the object as the last item, lets call it always instead
        # mod.body.append(ast.Expr(value=ast.Name(id=self.nb_var_name, ctx=ast.Load())))

        source = ast.unparse(mod).replace('"', '\\"')
        cell.source = source
        return cell

    def _base_generate_md(self, metadata: Optional[dict] = None) -> Optional[NotebookNode]:
        return self._base_generate_md_meta(metadata=metadata)

    def __repr__(self) -> str:
        # Truncate the output for now
        return f"<{self.__class__.__name__}>"
