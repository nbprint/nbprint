from pathlib import Path
from typing import Dict, List, Union

from nbformat import NotebookNode
from omegaconf import DictConfig, OmegaConf
from pydantic import Field, PrivateAttr, validator

from .base import BaseModel, Type
from .content import Content
from .context import Context
from .layout import LayoutGlobal
from .outputs import Outputs
from .parameters import Parameters
from .utils import SerializeAsAny, _append_or_extend


class Configuration(BaseModel):
    resources: Dict[str, SerializeAsAny[BaseModel]] = Field(default_factory=dict)
    outputs: SerializeAsAny[Outputs]
    parameters: SerializeAsAny[Parameters]
    layout: SerializeAsAny[LayoutGlobal]
    context: SerializeAsAny[Context]
    content: List[SerializeAsAny[Content]] = Field(default_factory=list)

    # internals
    _nb_var_name: str = PrivateAttr(default="nbprint_config")

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

    @validator("layout", pre=True)
    def convert_layout_from_obj(cls, v):
        return BaseModel._to_type(v, LayoutGlobal)

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

    def generate(self, metadata: dict = None, config: "Configuration" = None) -> List[NotebookNode]:
        cells = []

        # start with parameters for papermill compat
        _append_or_extend(cells, self.parameters.generate(metadata=metadata, config=self))

        # now do the configuration itself
        _append_or_extend(cells, self._generate_self(metadata=metadata))

        # now do
        # context: SerializeAsAny[Context]
        _append_or_extend(cells, self.context.generate(metadata=metadata, config=self, parent=self))

        # resources: Dict[str, SerializeAsAny[BaseModel]] = Field(default_factory=dict)
        # cell.metadata.nbprint.resources = {k: v.json() for k, v in self.resources.items()}

        # outputs: SerializeAsAny[Outputs]

        # now setup the layout
        # layout: SerializeAsAny[Layout]
        _append_or_extend(cells, self.layout.generate(metadata=metadata, config=self, parent=self))

        # content: List[SerializeAsAny[Content]] = Field(default_factory=list)
        for i, content in enumerate(self.content):
            _append_or_extend(
                cells, content.generate(metadata=metadata, config=self, parent=self, attr="content", counter=i)
            )
        return cells

    def _generate_self(self, metadata: dict = None) -> NotebookNode:
        cell = super()._base_generate(metadata=metadata, config=None)
        cell.metadata.tags.append("nbprint:configuration")
        cell.metadata.nbprint.role = "configuration"
        cell.metadata.nbprint.ignore = True

        # omit the data
        cell.metadata.nbprint.data = ""

        # add resources
        # TODO do this or no?
        # cell.metadata.nbprint.resources = {k: v.json() for k, v in self.resources.items()}
        cell.metadata.nbprint.outputs = self.outputs.json()
        return cell

    def _generate_resources_cells(self, metadata: dict = None):
        cell = super()._base_generate(metadata=metadata, config=None)
        cell.metadata.tags.append("nbprint:resources")
        cell.metadata.nbprint.role = "resources"
        cell.metadata.nbprint.ignore = True

        # omit the data
        cell.metadata.nbprint.data = ""

        # add resources
        # mod = ast.Module(body=[], type_ignores=[])
        # for k, v in self.resources.items():
        #     # TODO
        #     ...
        return cell


def load(path_or_model: Union[str, Path, dict, Configuration]) -> Configuration:
    if isinstance(path_or_model, Configuration):
        return path_or_model

    if isinstance(path_or_model, str) and (path_or_model.endswith(".yml") or path_or_model.endswith(".yaml")):
        path_or_model = Path(path_or_model).resolve()

    if isinstance(path_or_model, Path):
        path_or_model = OmegaConf.load(path_or_model)

    if isinstance(path_or_model, DictConfig):
        container = OmegaConf.to_container(path_or_model, resolve=True, throw_on_missing=True)
        return Configuration(**container)

    raise TypeError(f"Path or model malformed: {path_or_model} {type(path_or_model)}")
