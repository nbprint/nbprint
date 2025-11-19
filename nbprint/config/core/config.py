from ast import literal_eval
from pathlib import Path
from pprint import pprint
from sys import version_info
from typing import Type, Union

from ccflow import CallableModel, ContextType, Flow, ResultType
from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from nbformat import NotebookNode, read as nb_read
from nbformat.v4 import new_notebook
from pkn import getSimpleLogger
from pydantic import Field, PrivateAttr, field_validator, model_validator
from typing_extensions import Self

from nbprint import __version__
from nbprint.config.base import BaseModel, Role, _append_or_extend
from nbprint.config.content import Content, ContentCode, ContentMarkdown
from nbprint.config.exceptions import NBPrintPathIsYamlError, NBPrintPathOrModelMalformedError
from nbprint.config.page import Page

from .content import ContentMarshall
from .context import Context
from .outputs import Outputs, OutputsProcessing
from .parameters import PapermillParameters, Parameters

__all__ = (
    "Configuration",
    "load",
)

_log = getSimpleLogger("nbprint.config.core.config")


class Configuration(CallableModel, BaseModel):
    name: str
    resources: dict[str, BaseModel] = Field(default_factory=dict)
    outputs: Outputs
    parameters: Parameters = Field(default_factory=Parameters)
    page: Page = Field(default_factory=Page)
    context: Context = Field(default_factory=Context)

    content: ContentMarshall = Field(default_factory=ContentMarshall)

    # basic metadata
    tags: list[str] = Field(default_factory=list)
    role: Role = Role.CONFIGURATION
    ignore: bool = True
    pagedjs: bool = True
    debug: bool = True

    # internals
    _multi: bool = PrivateAttr(default=False)
    _nb_var_name: str = PrivateAttr(default="nbprint_config")
    _nb_vars: set = PrivateAttr(default_factory=set)

    @field_validator("tags", mode="after")
    @classmethod
    def _ensure_tags(cls, v: list[str]) -> list[str]:
        if "nbprint:config" not in v:
            v.append("nbprint:config")
        return v

    @field_validator("resources", mode="before")
    @classmethod
    def _convert_resources_from_obj(cls, value) -> dict[str, BaseModel]:
        if value is None:
            value = {}
        if isinstance(value, dict):
            for k, v in value.items():
                value[k] = BaseModel._to_type(v)
        return value

    @field_validator("outputs", mode="before")
    @classmethod
    def _convert_outputs_from_obj(cls, v) -> Outputs:
        return BaseModel._to_type(v, Outputs)

    @field_validator("parameters", mode="before")
    @classmethod
    def _convert_parameters_from_obj(cls, v) -> Parameters:
        return BaseModel._to_type(v, Parameters)

    @field_validator("page", mode="before")
    @classmethod
    def _convert_page_from_obj(cls, v) -> Page:
        return BaseModel._to_type(v, Page)

    @field_validator("context", mode="before")
    @classmethod
    def _convert_context_from_obj(cls, v) -> Context:
        return BaseModel._to_type(v, Context)

    @staticmethod
    def _convert_content_from_list(v) -> ContentMarshall:
        for i, element in enumerate(v):
            if isinstance(element, str):
                v[i] = Content(type_=element)
            elif isinstance(element, dict):
                v[i] = BaseModel._to_type(element)
        return ContentMarshall(middlematter=v)

    @staticmethod
    def _convert_content_from_dict(v) -> ContentMarshall:
        for key in ContentMarshall.model_fields:
            if key in v and isinstance(v[key], list):
                v[key] = Configuration._convert_content_from_list(v[key]).all
        return ContentMarshall(**v)

    @field_validator("content", mode="before")
    @classmethod
    def convert_content_from_obj(cls, v) -> ContentMarshall:
        if v is None:
            return ContentMarshall()
        if isinstance(v, list):
            return cls._convert_content_from_list(v)
        if isinstance(v, dict):
            return cls._convert_content_from_dict(v)
        return v

    @model_validator(mode="after")
    def _attach_params_to_context(self) -> Self:
        self.context.parameters = self.parameters
        return self

    @staticmethod
    def _init_content(values) -> ContentMarshall:
        if "content" not in values:
            values["content"] = ContentMarshall()
        elif isinstance(values["content"], list):
            values["content"] = ContentMarshall(middlematter=values["content"])
        elif isinstance(values["content"], dict):
            values["content"] = ContentMarshall(**values["content"])
        else:
            e = f"Unexpected content format when loading from notebook: {type(values['content'])}"
            raise RuntimeError(e)

    @staticmethod
    def _cell_to_content(cell) -> Content:
        source = cell.source.strip()
        if not source:
            # skip empty cells
            return None
        # Cells may have nbprint metadata from the UI extension
        # "nbprint": {
        #     "attrs": "",
        #     "class": "",
        #     "class_selector": "",
        #     "css": "",
        #     "data": "{}",
        #     "element_selector": "",
        #     "esm": "",
        #     "id": "",
        #     "ignore": true,
        #     "role": "parameters",
        #     "type_": "nbprint.config.core.parameters.Parameters"
        #    },
        if "metadata" in cell and "nbprint" in cell["metadata"]:
            nbprint_cell_meta = cell["metadata"]["nbprint"]

            # TODO: not all fields are serdes symmetric
            nbprint_cell_meta.pop("attrs", None)
            nbprint_cell_meta.pop("class", None)
            nbprint_cell_meta.pop("class_selector", None)
            nbprint_cell_meta.pop("element_selector", None)
        else:
            nbprint_cell_meta = {}

        # Attach cell tags in to content
        if "tags" in cell["metadata"]:
            nbprint_cell_meta["tags"] = cell["metadata"]["tags"]

        # If this is an nbprint defined type, use that
        if "type_" in nbprint_cell_meta:
            content_type = nbprint_cell_meta["type_"]
            content_model = BaseModel._to_type({"type_": content_type}, Content)
            return content_model.model_validate(nbprint_cell_meta)

        # Set source
        nbprint_cell_meta["content"] = cell.source

        # Default handling: treat as code or markdown content
        if cell.cell_type in {"code"}:
            content = ContentCode.model_validate(nbprint_cell_meta)
        elif cell.cell_type in {"markdown"}:
            content = ContentMarkdown.model_validate(nbprint_cell_meta)
        else:
            # Skip, log warning
            _log.warning(f"Unsupported cell type when loading from notebook: {cell.cell_type}")
        return content

    @staticmethod
    def _parse_parameters_cell(cell) -> dict:
        new_parameters = {}
        param_lines = cell.source.splitlines()
        for line in param_lines:
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                # Attempt to eval the value to get correct type
                try:
                    evaluated_value = literal_eval(value)
                except SyntaxError:
                    evaluated_value = value

                new_parameters[key] = evaluated_value
        return new_parameters

    @staticmethod
    def _process_cells(values, nb_content: NotebookNode) -> None:
        new_parameters = {}
        cells_to_process = nb_content.cells

        # TODO: if first cell has tags, insert at front instead of appending
        if cells_to_process and "metadata" in cells_to_process[0] and "parameters" in cells_to_process[0]["metadata"].get("tags", []):
            # Parse first cell for parameters
            first_cell = cells_to_process[0]
            # skip first cell
            cells_to_process = cells_to_process[1:]

            # Pull out the parameters object and ensure everything is present
            if "parameters" not in values:
                values["parameters"] = PapermillParameters()

            # Pull out the parameters object and ensure everything is present
            new_parameters = Configuration._parse_parameters_cell(first_cell)
        else:
            cells_to_process = nb_content.cells

        for cell in cells_to_process:
            cell_instance = Configuration._cell_to_content(cell)
            if cell_instance is not None:
                values["content"].middlematter.append(cell_instance)

        for k, v in new_parameters.items():
            if k in values["parameters"].model_fields and getattr(values["parameters"], k) is None:
                setattr(values["parameters"], k, v)
            elif isinstance(values["parameters"], PapermillParameters) and (k not in values["parameters"].vars or values["parameters"].vars[k] is None):
                values["parameters"].vars[k] = v

    @model_validator(mode="before")
    @classmethod
    def _append_notebook_content(cls, values) -> None:
        if values.get("notebook") is None:
            return values

        cls._init_content(values)

        file = Path(values.pop("notebook"))
        with file.open("r", encoding="utf-8") as path_file:
            nb_content = nb_read(path_file, as_version=4)

        cls._process_cells(values, nb_content)

        return values

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
        for i, content in enumerate(self.content.all):
            _append_or_extend(
                nb.cells,
                content.generate(metadata=base_meta.copy(), config=self, parent=self, attr="content", counter=i),
            )

        # Finally, run the outputs cell
        # NOTE: outputs cell doesnt usually actually do anything, unless
        # it is set to run in-context, in which case it will only
        # execute inside the notebook and note outside
        _append_or_extend(nb.cells, self.outputs.generate(metadata=base_meta.copy(), config=self, parent=self, attr="outputs"))

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

    def _generate_resources_cells(self, metadata: dict | None = None) -> NotebookNode:
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

        if isinstance(path_or_model, str) and path_or_model.endswith(".yml"):
            raise NBPrintPathIsYamlError(path_or_model)

        if isinstance(path_or_model, str) and path_or_model.endswith(".yaml"):
            path_or_model = Path(path_or_model).resolve()

        if isinstance(path_or_model, Path):
            path_or_model = path_or_model.resolve()
            folder = str(path_or_model.parent)
            file = str(path_or_model.name)

            with initialize_config_dir(version_base=None, config_dir=folder, job_name=name):
                cfg = compose(config_name=file, overrides=[f"+name={name}"])
                config = instantiate(cfg, _convert_="all")
                if not isinstance(config, Configuration):
                    config = Configuration.model_validate(config)
                return config
        raise NBPrintPathOrModelMalformedError(path_or_model)

    def run(self, dry_run: bool = False, *, _multi: bool = False) -> Path | None:
        gen = self.generate()
        ret = None
        if self.debug:
            pprint(gen)
        if not dry_run:
            ret = self.outputs.run(self, gen)
            if ret in (None, OutputsProcessing.STOP):
                # Either a handled problem or user requested stop
                # Return None to indicate a problem
                # TODO: revisit
                return None

        if not self._multi and self.outputs.postprocess:
            # Run postprocessing
            self.outputs.postprocess.object([self])

            # NOTE: as of this point, we're "done"

            # reset in case we want to run again
            self._reset()
        return ret

    def _reset(self) -> None:
        # reset ourselves in case we need to rerun
        self._nb_vars = set()
        self.context._context_generated = False

    # ccflow integration
    @property
    def context_type(self) -> Type[ContextType]:
        return self.parameters.__class__

    @property
    def result_type(self) -> Type[ResultType]:
        return self.outputs.__class__

    @Flow.call
    def __call__(self, context):  # noqa: ANN204
        # NOTE: make a copy to avoid mutation during flow runs interfering with caching
        # update parameters if changed
        if context != self.parameters:
            self.parameters = context
            self._reset()
        self.run()
        return self.outputs


load = Configuration.load
