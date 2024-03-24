from nbformat import NotebookNode
from nbformat.v4 import new_notebook
from omegaconf import DictConfig, OmegaConf
from pathlib import Path
from pprint import pprint
from pydantic import Field, PrivateAttr, validator
from sys import version_info
from typing import Dict, List, Union

from ... import __version__
from ..base import BaseModel, Role, Type, _append_or_extend
from ..content import Content
from ..page import PageGlobal
from .context import Context
from .outputs import Outputs
from .parameters import Parameters


class Configuration(BaseModel):
    name: str
    resources: Dict[str, BaseModel] = Field(default_factory=dict)
    outputs: Outputs
    parameters: Parameters
    page: PageGlobal
    context: Context
    content: List[Content] = Field(default_factory=list)

    # basic metadata
    tags: List[str] = Field(default=["nbprint:config"])
    role: Role = Role.CONFIGURATION
    ignore: bool = True
    debug: bool = True

    # internals
    _nb_var_name: str = PrivateAttr(default="nbprint_config")
    _nb_vars: set = PrivateAttr(default_factory=set)

    @validator("resources", pre=True)
    def convert_resources_from_obj(cls, value):
        if value is None:
            value = {}
        if isinstance(value, dict):
            for k, v in value.items():
                value[k] = BaseModel._to_type(v)
        return value

    @validator("outputs", pre=True)
    def convert_outputs_from_obj(cls, v):
        return BaseModel._to_type(v, Outputs)

    @validator("parameters", pre=True)
    def convert_parameters_from_obj(cls, v):
        return BaseModel._to_type(v, Parameters)

    @validator("page", pre=True)
    def convert_page_from_obj(cls, v):
        return BaseModel._to_type(v, PageGlobal)

    @validator("context", pre=True)
    def convert_context_from_obj(cls, v):
        return BaseModel._to_type(v, Context)

    @validator("content", pre=True)
    def convert_content_from_obj(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            for i, element in enumerate(v):
                if isinstance(element, str):
                    v[i] = Content(type=Type.from_string(element))
                elif isinstance(element, dict):
                    v[i] = BaseModel._to_type(element)
        return v

    def generate(self, extra_metadata: dict = None) -> List[NotebookNode]:
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
        _append_or_extend(
            nb.cells, self.context.generate(metadata=base_meta.copy(), config=self, parent=self, attr="context")
        )

        # resources: Dict[str, SerializeAsAny[BaseModel]] = Field(default_factory=dict)
        # TODO omitting resources, referenced directly in yaml
        # cell.metadata.nbprint.resources = {k: v.json() for k, v in self.resources.items()}

        # outputs: SerializeAsAny[Outputs]
        # TODO skipping, consumed internally

        # now setup the page layout
        # pass in parent=self, attr=page so we do config.page
        _append_or_extend(
            nb.cells, self.page.generate(metadata=base_meta.copy(), config=self, parent=self, attr="page")
        )

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

        # add resources
        # TODO do this or no?
        # cell.metadata.nbprint.resources = {k: v.json() for k, v in self.resources.items()}
        cell.metadata.nbprint.outputs = self.outputs.json()
        return cell

    def _generate_resources_cells(self, metadata: dict = None):
        cell = super()._base_generate(metadata=metadata, config=None)

        # omit the data
        cell.metadata.nbprint.data = ""

        # add resources
        # mod = ast.Module(body=[], type_ignores=[])
        # for k, v in self.resources.items():
        #     # TODO
        #     ...
        return cell

    @staticmethod
    def load(path_or_model: Union[str, Path, dict, "Configuration"], name: str) -> "Configuration":
        if isinstance(path_or_model, Configuration):
            return path_or_model

        if isinstance(path_or_model, str) and (path_or_model.endswith(".yml") or path_or_model.endswith(".yaml")):
            path_or_model = Path(path_or_model).resolve()

        if isinstance(path_or_model, Path):
            path_or_model = OmegaConf.load(path_or_model)

        if isinstance(path_or_model, DictConfig):
            container = OmegaConf.to_container(path_or_model, resolve=True, throw_on_missing=True)
            return Configuration(name=name, **container)

        raise TypeError(f"Path or model malformed: {path_or_model} {type(path_or_model)}")

    def run(self, debug: bool = True):
        gen = self.generate(self)
        if debug:
            pprint(gen)
        self.outputs.run(self, gen)


load = Configuration.load
