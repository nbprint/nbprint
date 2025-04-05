from pathlib import Path
from pprint import pprint
from sys import version_info
from typing import Optional, Union

from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from nbformat import NotebookNode
from nbformat.v4 import new_notebook
from pydantic import Field, PrivateAttr, field_validator, model_validator
from typing_extensions import Self

from nbprint import __version__
from nbprint.config.base import BaseModel, Role, _append_or_extend
from nbprint.config.content import Content
from nbprint.config.exceptions import NBPrintPathOrModelMalformedError
from nbprint.config.page import Page

from .context import Context
from .outputs import Outputs
from .parameters import Parameters

__all__ = (
    "Configuration",
    "load",
)


class Configuration(BaseModel):
    name: str
    resources: dict[str, BaseModel] = Field(default_factory=dict)
    outputs: Outputs
    parameters: Parameters = Field(default_factory=Parameters)
    page: Page = Field(default_factory=Page)
    context: Context = Field(default_factory=Context)
    content: list[Content] = Field(default_factory=list)

    # basic metadata
    tags: list[str] = Field(default=["nbprint:config"])
    role: Role = Role.CONFIGURATION
    ignore: bool = True
    pagedjs: bool = True
    debug: bool = True

    # internals
    _nb_var_name: str = PrivateAttr(default="nbprint_config")
    _nb_vars: set = PrivateAttr(default_factory=set)

    @field_validator("resources", mode="before")
    @classmethod
    def convert_resources_from_obj(cls, value) -> dict[str, BaseModel]:
        if value is None:
            value = {}
        if isinstance(value, dict):
            for k, v in value.items():
                value[k] = BaseModel._to_type(v)
        return value

    @field_validator("outputs", mode="before")
    @classmethod
    def convert_outputs_from_obj(cls, v) -> Outputs:
        return BaseModel._to_type(v, Outputs)

    @field_validator("parameters", mode="before")
    @classmethod
    def convert_parameters_from_obj(cls, v) -> Parameters:
        return BaseModel._to_type(v, Parameters)

    @field_validator("page", mode="before")
    @classmethod
    def convert_page_from_obj(cls, v) -> Page:
        return BaseModel._to_type(v, Page)

    @field_validator("context", mode="before")
    @classmethod
    def convert_context_from_obj(cls, v) -> Context:
        return BaseModel._to_type(v, Context)

    @field_validator("content", mode="before")
    @classmethod
    def convert_content_from_obj(cls, v) -> Content:
        if v is None:
            return []
        if isinstance(v, list):
            for i, element in enumerate(v):
                if isinstance(element, str):
                    v[i] = Content(type_=element)
                elif isinstance(element, dict):
                    v[i] = BaseModel._to_type(element)
        return v

    @model_validator(mode="after")
    def _attach_params_to_context(self) -> Self:
        self.context.parameters = self.parameters
        return self

    def generate(self, **_) -> list[NotebookNode]:
        nb = new_notebook()
        nb.metadata.nbprint = {}
        nb.metadata.nbprint.version = __version__
        nb.metadata.nbprint.tags = []
        nb.metadata.nbprint.nbprint = {}
        nb.metadata.nbprint.language = f"python{version_info.major}.{version_info.minor}"

        base_meta = {
            "tags": [],
            "nbprint": {},
        }

        nb.cells = []

        # start with parameters for papermill compat
        # use `parent=None` because we parameters is first cell, and we wont instantiate the config
        # until the next cell
        _append_or_extend(nb.cells, self.parameters.generate(metadata=base_meta.copy(), config=self, parent=None))

        # now do the configuration itself
        _append_or_extend(nb.cells, self._generate_self(metadata=base_meta.copy()))

        # now do the context object
        # pass in parent=self, attr=context so we do config.context
        _append_or_extend(nb.cells, self.context.generate(metadata=base_meta.copy(), config=self, parent=self, attr="context"))

        # resources: dict[str, SerializeAsAny[BaseModel]] = Field(default_factory=dict)
        # TODO: omitting resources, referenced directly in yaml
        # cell.metadata.nbprint.resources = {k: v.model_dump_json(by_alias=True) for k, v in self.resources.items()}

        # outputs: SerializeAsAny[Outputs]
        # TODO: skipping, consumed internally

        # now setup the page layout
        # pass in parent=self, attr=page so we do config.page
        _append_or_extend(nb.cells, self.page.generate(metadata=base_meta.copy(), config=self, parent=self, attr="page"))

        # now iterate through the content, recursively generating
        for i, content in enumerate(self.content):
            _append_or_extend(
                nb.cells,
                content.generate(metadata=base_meta.copy(), config=self, parent=self, attr="content", counter=i),
            )

        return nb

    def _generate_self(self, metadata: dict) -> NotebookNode:
        cell = super()._base_generate(metadata=metadata, config=self)

        # omit the data
        cell.metadata.nbprint.data = ""

        # add extras
        cell.metadata.nbprint.debug = self.debug
        cell.metadata.nbprint.pagedjs = self.pagedjs

        # add resources
        # TODO: do this or no?
        # cell.metadata.nbprint.resources = {k: v.model_dump_json(by_alias=True) for k, v in self.resources.items()}
        cell.metadata.nbprint.outputs = self.outputs.model_dump_json(by_alias=True)
        return cell

    def _generate_resources_cells(self, metadata: Optional[dict] = None) -> NotebookNode:
        cell = super()._base_generate(metadata=metadata, config=None)

        # omit the data
        cell.metadata.nbprint.data = ""

        # add resources
        # mod = ast.Module(body=[], type_ignores=[])
        # for k, v in self.resources.items():
        #     ...
        return cell

    @staticmethod
    def load(path_or_model: Union[str, Path, dict, "Configuration"], name: str) -> "Configuration":
        if isinstance(path_or_model, Configuration):
            return path_or_model

        if isinstance(path_or_model, str) and path_or_model.endswith((".yml", ".yaml")):
            path_or_model = Path(path_or_model).resolve()

        if isinstance(path_or_model, Path):
            path_or_model = path_or_model.resolve()
            folder = str(path_or_model.parent)
            file = str(path_or_model.name)

            with initialize_config_dir(version_base=None, config_dir=folder, job_name=name):
                cfg = compose(config_name=file, overrides=[f"+name={name}"])
                config = instantiate(cfg, _convert_="all")
                if not isinstance(config, Configuration):
                    config = Configuration(**config)
                return config
        raise NBPrintPathOrModelMalformedError(path_or_model)

    def run(self, dry_run: bool = False) -> Optional[Path]:
        gen = self.generate()
        ret = None
        if self.debug:
            pprint(gen)
        if not dry_run:
            ret = self.outputs.run(self, gen)

        # reset in case we want to run again
        self._reset()
        return ret

    def _reset(self) -> None:
        # reset ourselves in case we need to rerun
        self._nb_vars = set()
        self.context._context_generated = False


load = Configuration.load
