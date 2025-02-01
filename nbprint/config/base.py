import ast
from collections.abc import Mapping
from json import dumps, loads
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Union
from uuid import uuid4

from ccflow import BaseModel as FlowBaseModel, PyObjectPath
from IPython.display import DisplayObject
from nbformat import NotebookNode
from nbformat.v4 import new_code_cell, new_markdown_cell
from pydantic import Field, PrivateAttr, field_validator
from strenum import StrEnum

if TYPE_CHECKING:
    from nbprint.config import Configuration

__all__ = (
    "BaseModel",
    "Role",
    "_append_or_extend",
)


class Role(StrEnum):
    UNDEFINED = "undefined"
    CONFIGURATION = "configuration"
    CONTEXT = "context"
    OUTPUTS = "outputs"
    PARAMETERS = "parameters"
    CONTENT = "content"
    PAGE = "page"
    LAYOUT = "layout"


class BaseModel(FlowBaseModel):
    # basic metadata
    tags: List[str] = Field(default_factory=list)
    role: Role = Role.UNDEFINED
    ignore: bool = False

    # frontend code
    # This is designed to match anywidget
    css: Optional[Union[str, Path]] = Field(default="")
    esm: Optional[Union[str, Path]] = Field(default="")
    classname: Optional[Union[str, list[str]]] = Field(default="")
    attrs: Optional[Mapping[str, str]] = Field(default_factory=dict)

    # internals
    # Variable to use inside notebook for this model
    _nb_var_name: Optional[str] = PrivateAttr(default="")

    # id to use to reconstitute dom during page building
    _id: str = PrivateAttr(default_factory=lambda: str(uuid4()).replace("-", ""))

    class Config:
        """Pydantic configuration object."""

        arbitrary_types_allowed: bool = False
        extra: str = "ignore"
        validate_assignment: bool = True

    def __init__(self, **kwargs) -> None:
        if "_target_" not in kwargs:
            kwargs["_target_"] = f"{self.__class__.__module__}.{self.__class__.__name__}"
        super().__init__(**kwargs)

    @field_validator("css", mode="before")
    @classmethod
    def convert_css_string_or_path_to_string_or_path(cls, v) -> str:
        if isinstance(v, str) and v.strip().endswith(".css"):
            # TODO: resolve relative to class?
            v = Path(v).resolve().read_text()
        return v

    @field_validator("esm", mode="before")
    @classmethod
    def convert_esm_string_or_path_to_string_or_path(cls, v) -> str:
        if isinstance(v, str):
            v = v.strip()
            if v.endswith((".js", ".mjs")):
                # TODO: resolve relative to class?
                v = Path(v).resolve().read_text()
        return v

    @property
    def nb_var_name(self) -> str:
        if self._nb_var_name:
            return self._nb_var_name
        name = self.__class__.__name__.lower()
        if name.startswith("nbprint"):
            return name.replace("nbprint", "nbprint_")
        return f"nbprint_{name}"

    def _recalculate_nb_var_name(self, nb_vars: set) -> None:
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
    def _to_type(value, model_type=None) -> "BaseModel":
        if value is None:
            value = {}

        if "_target_" in value:
            # derive type from instantiation
            model_type = PyObjectPath(value["_target_"]).object
        elif model_type is None:
            model_type = BaseModel

        if isinstance(value, dict):
            return model_type(**value)

        return value

    @classmethod
    def from_json(cls, json) -> "BaseModel":
        data = loads(json)
        return cls(**data)

    def __call__(self, **_) -> Optional[DisplayObject]:
        """Execute this model inside of a notebook

        Args:
        ----
            ctx (_type_, optional): _description_. Defaults to None.

        """
        return self

    def render(self, **_) -> None:
        """Called during notebook generation only, this should run any necessary post-processing. Pre-processing should go in __init__"""

    def generate(
        self,
        metadata: dict,
        config: Optional["Configuration"],
        parent: Optional["BaseModel"] = None,
        attr: str = "",
        counter: Optional[int] = None,
        **_,
    ) -> Optional[Union[NotebookNode, list[NotebookNode]]]:
        """Generate a notebook node for this model.
        This will be called before the runtime of the notebook, use it for code generation.

        Args:
        ----
            metadata (dict): common cell metadata

        Returns:
        -------
            NotebookNode: the content of the notebook node

        """
        return self._base_generate(metadata=metadata, config=config, parent=parent, attr=attr, counter=counter)

    def _base_set_nbprint_metadata(self, cell: NotebookNode) -> None:
        cell.metadata.nbprint.id = self._id
        cell.metadata.nbprint.role = self.role or "undefined"
        cell.metadata.nbprint.type_ = str(self.type_)
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
        cell.metadata.nbprint.class_selector = f"{cell.metadata.nbprint.type_.replace('.', '-')}"
        cell.metadata.nbprint.element_selector = f"{cell.metadata.nbprint.class_selector}-{self._id}"
        cell.metadata.nbprint["class"] = f"nbprint {cell.metadata.nbprint.class_selector} {cell.metadata.nbprint.element_selector} " + (
            " ".join(self.classname) if isinstance(self.classname, list) else self.classname or ""
        )
        cell.metadata.nbprint.attrs = " ".join(f"{k}={dumps(v)}" for k, v in (self.attrs or {}).items())

    def _base_generate_meta(self, metadata: Optional[dict] = None) -> Optional[NotebookNode]:
        cell = new_code_cell(metadata=metadata)
        cell.metadata.tags = list(set(["nbprint"] + (self.tags or [])))

        # TODO: consolidate with self.model_dump_json(by_alias=True)?
        self._base_set_nbprint_metadata(cell)
        cell.metadata.nbprint.data = self.model_dump_json(by_alias=True)
        return cell

    def _base_generate_md_meta(self, metadata: Optional[dict] = None) -> Optional[NotebookNode]:
        cell = new_markdown_cell(metadata=metadata)
        cell.metadata.tags = list(set(["nbprint"] + (self.tags or [])))
        self._base_set_nbprint_metadata(cell)
        return cell

    def _base_generate(
        self,
        metadata: dict,
        config: "Configuration",
        parent: Optional["BaseModel"] = None,
        attr: str = "",
        counter: Optional[int] = None,
    ) -> Optional[NotebookNode]:
        from nbprint.config import Configuration

        # trigger any pre-cell generation logic
        self.render(config=config)

        cell = self._base_generate_meta(metadata=metadata)
        mod = ast.Module(body=[], type_ignores=[])

        assert config is not None
        self._recalculate_nb_var_name(config._nb_vars)

        if parent and parent.ignore is False:
            # TODO: should this go in a standard location?
            # set in metadata
            cell.metadata.nbprint["parent-id"] = parent._id

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
            module, name = str(self.type_).rsplit(".", 1)
            mod.body.append(
                ast.ImportFrom(
                    module=module,
                    names=[ast.alias(name=name)],
                    level=0,
                )
            )

            mod.body.append(
                ast.Assign(
                    targets=[ast.Name(id=self.nb_var_name, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Attribute(value=ast.Name(id=name, ctx=ast.Load()), attr="from_json", ctx=ast.Load()),
                        args=[ast.parse(dumps(data), mode="eval").body],
                        keywords=[],
                    ),
                    lineno=2,
                )
            )

        # Determine whether to pass context into the call.
        # If we have a config object, and that config object has a context, and we've previously made the context object,
        # and we ourselves are not a config, then pass in
        call_with_context = (
            config.context.nb_var_name
            if config and config.context and config.context._context_generated and not isinstance(self, Configuration)
            else "None"
        )

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

    def _base_generate_md(self, metadata: dict, config: "Configuration", parent: Optional["BaseModel"] = None) -> Optional[NotebookNode]:
        # trigger any pre-cell generation logic
        self.render(config=config)

        cell = self._base_generate_md_meta(metadata=metadata)
        # TODO: should this go in a standard location?
        # set in metadata
        if parent and parent.ignore is False:
            cell.metadata.nbprint["parent-id"] = parent._id
        return cell

    def __repr__(self) -> str:
        # Truncate the output for now
        return f"<{self.__class__.__name__}>"


def _append_or_extend(cells: list, cell_or_cells: Union[NotebookNode, list[NotebookNode]]) -> None:
    if isinstance(cell_or_cells, list):
        cells.extend(cell_or_cells)
    elif cell_or_cells:
        cells.append(cell_or_cells)
    # None, ignore
