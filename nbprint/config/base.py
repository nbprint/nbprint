from __future__ import annotations

import ast
from importlib import import_module
from IPython.display import DisplayObject
from json import dumps, loads
from nbformat import NotebookNode
from nbformat.v4 import new_code_cell, new_markdown_cell
from pathlib import Path
from pydantic import BaseModel, Field, PrivateAttr, SerializeAsAny, field_validator
from pydantic._internal._model_construction import ModelMetaclass
from strenum import StrEnum
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    from nbprint.config import Configuration

__all__ = (
    "Type",
    "Role",
    "BaseModel",
    "_append_or_extend",
)


# https://github.com/pydantic/pydantic/issues/6423#issuecomment-1967475432
class _SerializeAsAnyMeta(ModelMetaclass):
    def __new__(cls, name: str, bases: tuple[type], namespaces: dict[str, Any], **kwargs) -> type:
        annotations: dict = namespaces.get("__annotations__", {}).copy()
        for field, annotation in annotations.items():
            if not field.startswith("__"):
                annotations[field] = SerializeAsAny[annotation]
        namespaces["__annotations__"] = annotations
        return super().__new__(cls, name, bases, namespaces, **kwargs)


class Type(BaseModel):
    """Class to represent any pydantic BaseModel type, using import module and class name."""

    module: str
    name: str

    @classmethod
    def from_string(cls, st: str) -> Type:
        """Helper method to get type from string."""
        module, name = st.rsplit(".", 1)
        return Type(module=module, name=name)

    def to_string(self) -> str:
        """Helper method to create string from module and type."""
        return f"{self.module}:{self.name}"

    def type(self) -> type[Type]:
        """Import module and access type."""
        return getattr(import_module(self.module), self.name)

    def load(self, **kwargs) -> Type:
        """Instantiate instance from type."""
        return self.type()(**kwargs)


class Role(StrEnum):
    """Enumeration of the various well-defined roles that models can play in a report."""

    UNDEFINED = "undefined"
    CONFIGURATION = "configuration"
    CONTEXT = "context"
    OUTPUTS = "outputs"
    PARAMETERS = "parameters"
    CONTENT = "content"
    PAGE = "page"
    LAYOUT = "layout"


class BaseModel(BaseModel, metaclass=_SerializeAsAnyMeta):
    """Base class of all nbprint types, pydantic model with hydra-compatible serialization and notebook cell generation ability."""

    # type info
    type: Type = Field(alias="_target_")

    # basic metadata
    tags: list[str] = Field(default_factory=list)
    role: Role = Role.UNDEFINED
    ignore: bool = False

    # frontend code
    # This is designed to match anywidget
    css: str | Path | None = Field(default="")
    esm: str | Path | None = Field(default="")
    classname: str | list[str] | None = Field(default="")
    attrs: dict[str, str] | None = Field(default_factory=dict)

    # internals
    # Variable to use inside notebook for this model
    _nb_var_name: str | None = PrivateAttr(default="")

    # id to use to reconstitute dom during page building
    _id: str = PrivateAttr(default_factory=lambda: str(uuid4()).replace("-", ""))

    class Config:
        """Pydantic Model configuration."""

        arbitrary_types_allowed: bool = False
        extra: str = "ignore"
        validate_assignment: bool = True

    def __init__(self, **kwargs) -> None:
        """Contruct BaseModel object from its type and arguments."""
        if "_target_" not in kwargs:
            kwargs["_target_"] = Type(module=self.__class__.__module__, name=self.__class__.__name__)
        super().__init__(**kwargs)

    @field_validator("css", mode="before")
    @classmethod
    def convert_css_string_or_path_to_string_or_path(cls, v: str) -> str:
        """Helper method to convert string or path to css file to string."""
        if isinstance(v, str) and v.strip().endswith(".css"):
            # TODO: resolve relative to class?
            v = Path(v).resolve().read_text()
        return v

    @field_validator("esm", mode="before")
    @classmethod
    def convert_esm_string_or_path_to_string_or_path(cls, v: str) -> str:
        """Helper method to convert string or path to js/mjs file to string."""
        if isinstance(v, str):
            v = v.strip()
            if v.endswith((".js", ".mjs")):
                # TODO: resolve relative to class?
                v = Path(v).resolve().read_text()
        return v

    @field_validator("type", mode="before")
    @classmethod
    def convert_type_string_to_module_and_name(cls, v: str) -> Type:
        """Helper method to get module and type name from string."""
        if isinstance(v, str):
            return Type.from_string(v)
        return v

    @property
    def nb_var_name(self) -> str:
        """Helper property to determine what variable to store an instance in, inside a notebook."""
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
    def _to_type(value, model_type: Type = None) -> BaseModel:
        if value is None:
            value = {}

        if model_type is None and "_target_" in value:
            # derive type from instantiation
            model_type = BaseModel

        if isinstance(value, dict):
            return model_type(**value).type.load(**value)

        return value

    @classmethod
    def from_json(cls, json: str) -> BaseModel:
        """Helper method to load class from json string."""
        data = loads(json)
        return cls(**data)

    def __call__(self, *_, **__) -> DisplayObject | None:
        """Execute this model inside of a notebook.

        Args:
        ----
            ctx (_type_, optional): _description_. Defaults to None.

        """
        return self

    def render(self, config: Configuration) -> None:
        """Called during notebook generation only, this should run any necessary post-processing. Pre-processing should go in __init__."""

    def generate(  # noqa: PLR0913
        self,
        metadata: dict,
        config: Configuration | None,
        parent: BaseModel | None = None,
        attr: str = "",
        counter: int | None = None,
    ) -> NotebookNode | list[NotebookNode] | None:
        """Generate a notebook node for this model.

        This will be called before the runtime of the notebook, use it for code generation.

        Args:
        ----
            metadata (dict): common cell metadata
            config (Configuration): configuration object
            parent (BaseModel): Parent element in config hierarchy
            attr (str): Attr on parent on which this element lives, e.g. parent.child -> "child"
            counter (int): Index in side parent element, e.g. parent.children[1] -> 1

        Returns:
        -------
            NotebookNode: the content of the notebook node

        """
        return self._base_generate(metadata=metadata, config=config, parent=parent, attr=attr, counter=counter)

    def _base_set_nbprint_metadata(self, cell: NotebookNode):
        cell.metadata.nbprint.id = self._id
        cell.metadata.nbprint.role = self.role or "undefined"
        cell.metadata.nbprint.type = self.type.to_string()
        cell.metadata.nbprint.ignore = self.ignore or False
        if cell.metadata.nbprint.ignore and self.role in (Role.PARAMETERS,):
            # Don't collapse
            ...
        elif cell.metadata.nbprint.ignore or self.role in (
            Role.CONFIGURATION,
            Role.CONTEXT,
            Role.PAGE,
            Role.UNDEFINED,
        ):
            # Collapse cell by default
            cell.metadata["jupyter"] = {
                "source_hidden": True,
                "outputs_hidden": True,
            }
            cell.metadata.collapsed = True
        cell.metadata.nbprint.css = self.css or ""
        cell.metadata.nbprint.esm = self.esm or ""
        cell.metadata.nbprint.class_selector = f'{cell.metadata.nbprint.type.replace(":", "-").replace(".", "-")}'
        cell.metadata.nbprint.element_selector = f"{cell.metadata.nbprint.class_selector}-{self._id}"
        cell.metadata.nbprint["class"] = f"nbprint {cell.metadata.nbprint.class_selector} {cell.metadata.nbprint.element_selector} " + (
            " ".join(self.classname) if isinstance(self.classname, list) else self.classname or ""
        )
        cell.metadata.nbprint.attrs = " ".join(f"{k}={dumps(v)}" for k, v in (self.attrs or {}).items())

    def _base_generate_meta(self, metadata: dict | None = None) -> NotebookNode | None:
        cell = new_code_cell(metadata=metadata)
        cell.metadata.tags = list(set(["nbprint"] + (self.tags or [])))

        # TODO: consolidate with self.model_dump_json(by_alias=True)?
        self._base_set_nbprint_metadata(cell)
        cell.metadata.nbprint.data = self.model_dump_json(by_alias=True)
        return cell

    def _base_generate_md_meta(self, metadata: dict | None = None) -> NotebookNode | None:
        cell = new_markdown_cell(metadata=metadata)
        cell.metadata.tags = list(set(["nbprint"] + (self.tags or [])))
        self._base_set_nbprint_metadata(cell)
        return cell

    def _base_generate(  # noqa: PLR0913
        self,
        metadata: dict,
        config: Configuration,
        parent: BaseModel | None = None,
        attr: str = "",
        counter: int | None = None,
    ) -> NotebookNode | None:
        # trigger any pre-cell generation logic
        self.render(config=config)

        cell = self._base_generate_meta(metadata=metadata)
        mod = ast.Module(body=[], type_ignores=[])

        assert config is not None  # noqa: S101
        self._recalculate_nb_var_name(config._nb_vars)  # noqa: SLF001

        if parent and parent.ignore is False:
            # TODO: should this go in a standard location?
            # set in metadata
            cell.metadata.nbprint["parent-id"] = parent._id  # noqa: SLF001

        if parent and attr:
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
            data = self.model_dump_json(by_alias=True)
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
                        func=ast.Attribute(value=ast.Name(id=self.type.name, ctx=ast.Load()), attr="from_json", ctx=ast.Load()),
                        args=[ast.parse(dumps(data), mode="eval").body],
                        keywords=[],
                    ),
                    lineno=2,
                )
            )

        call_with_context = config.context.nb_var_name if config and config.context and config.context._context_generated else "None"  # noqa: SLF001

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

    def _base_generate_md(self, metadata: dict, config: Configuration, parent: BaseModel | None = None) -> NotebookNode | None:
        # trigger any pre-cell generation logic
        self.render(config=config)

        cell = self._base_generate_md_meta(metadata=metadata)
        # TODO: should this go in a standard location?
        # set in metadata
        if parent and parent.ignore is False:
            cell.metadata.nbprint["parent-id"] = parent._id  # noqa: SLF001
        return cell

    def __repr__(self) -> str:
        """Create truncated repr of class name."""
        # Truncate the output for now
        return f"<{self.__class__.__name__}>"


def _append_or_extend(cells: list, cell_or_cells: NotebookNode | list[NotebookNode]) -> None:
    if isinstance(cell_or_cells, list):
        cells.extend(cell_or_cells)
    elif cell_or_cells:
        cells.append(cell_or_cells)
    # None, ignore
