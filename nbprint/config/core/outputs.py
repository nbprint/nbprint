from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from ccflow import PyObjectPath, ResultBase
from IPython.display import HTML
from jinja2 import Template
from nbformat import NotebookNode, writes
from pydantic import Field, PrivateAttr, field_validator, model_validator

from nbprint.config.base import BaseModel, Role

if TYPE_CHECKING:
    from .config import Configuration

__all__ = ("Outputs", "OutputsProcessing")


class OutputsProcessing(str, Enum):
    CONTINUE = "continue"
    STOP = "stop"


class Outputs(ResultBase, BaseModel):
    root: Path = Field(default=Path.cwd() / "outputs")
    naming: str = Field(default="{{name}}-{{date}}")

    tags: list[str] = Field(default_factory=list)
    role: Role = Role.OUTPUTS
    ignore: bool = True

    embedded: bool = Field(default=False, description="Whether this output is expected to run from its embedding inside the notebook.")
    hook: PyObjectPath | None = Field(
        default=None,
        description=(
            "A callable hook that is called after generation of the notebook. "
            "It is passed the config instance. "
            "If it returns something non-None, that value is returned by `run` instead of the output path."
        ),
    )
    postprocess: PyObjectPath | None = Field(
        default=None,
        description=(
            "A callable hook that is called after all processing completes. "
            "It is passed the config instance/s. "
            "NOTE: It may receive multiple Configuration instances, if a parameterized run was performed."
        ),
    )

    # Private variables to compute and store paths
    _nb_path: Path | None = PrivateAttr(default=None)
    _nb_executed_path: Path | None = PrivateAttr(default=None)
    _output_path: Path | None = PrivateAttr(default=None)

    @property
    def notebook(self) -> Path:
        return self._nb_path

    @property
    def executed_notebook(self) -> Path:
        return self._nb_executed_path

    @property
    def output(self) -> Path:
        return self._output_path

    @field_validator("tags", mode="after")
    @classmethod
    def _ensure_tags(cls, v: list[str]) -> list[str]:
        if "nbprint:outputs" not in v:
            v.append("nbprint:outputs")
        return v

    @field_validator("root", mode="before")
    @classmethod
    def _convert_str_to_path(cls, v) -> Path:
        if isinstance(v, str):
            v = Path(v)
        if isinstance(v, Path):
            return v
        raise TypeError

    @model_validator(mode="after")
    def _ensure_embedded_or_cells_not_both(self) -> "Outputs":
        if self.embedded and self.cells:
            err = "Cannot set both 'embedded' and 'cells'. If `embedded`, set fields on context object. Otherwise, select cells."
            raise ValueError(err)
        return self

    def _compute_outputs(self, config: "Configuration") -> None:
        name = Template(self.naming).render(
            name=self._get_name(config=config),
            date=self._get_date(config=config),
            datetime=self._get_datetime(config=config),
            uuid=self._get_uuid(config=config),
            sha=self._get_sha(config=config),
            **config.parameters.model_dump(exclude_none=True, exclude_unset=True),
        )

        root = Path(self.root).resolve()
        self._nb_executed_path = root / f"{name}.ipynb"
        self._nb_path = root / f"{name}.ipynb"
        self._output_path = root / f"{name}.ipynb"

    def _get_name(self, config: "Configuration") -> str:
        return config.name

    def _get_date(self, **_) -> str:
        return date.today().isoformat()

    def _get_datetime(self, **_) -> str:
        return datetime.now().isoformat()

    def _get_uuid(self, **_) -> str:
        return uuid4()

    def _get_sha(self, config: "Configuration") -> str:
        import hashlib

        return hashlib.sha256(config.model_dump_json(by_alias=True).encode()).hexdigest()

    def run(self, config: "Configuration", gen: NotebookNode) -> Path:
        # Create file or folder path
        if not self.notebook.parent.exists():
            self.notebook.parent.mkdir(parents=True, exist_ok=True)

        self.notebook.write_text(writes(gen), encoding="utf-8")

        if self.hook and self.hook.object(config) in (OutputsProcessing.STOP, None):
            return OutputsProcessing.STOP
        return self.notebook

    def generate(self, metadata: dict, **kwargs) -> NotebookNode:
        return super().generate(metadata=metadata, **kwargs)

    def __call__(self, **_) -> HTML:
        if self.embedded:
            # If we're running this code, the notebook is already executing.
            # For child classes, this might mean saving ourselves (the notebook
            # in which we're running), then running nbconvert on ourselves
            # with execute=False.
            #
            # For now, this is a TODO.
            err = "Outputs cell execution in context is not yet implemented."
            raise NotImplementedError(err)
        return HTML("")
