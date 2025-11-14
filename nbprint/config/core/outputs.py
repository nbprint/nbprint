from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from ccflow import ResultBase
from jinja2 import Template
from nbformat import NotebookNode, writes
from pydantic import Field, PrivateAttr, field_validator

from nbprint.config.base import BaseModel, Role

if TYPE_CHECKING:
    from .config import Configuration

__all__ = ("Outputs",)


class Outputs(ResultBase, BaseModel):
    path_root: Path = Field(default=Path.cwd() / "outputs")
    naming: str = Field(default="{{name}}-{{date}}")

    tags: list[str] = Field(default=["nbprint:outputs"])
    role: Role = Role.OUTPUTS
    ignore: bool = True

    _nb_path: Path | None = PrivateAttr(default=None)
    _output_path: Path | None = PrivateAttr(default=None)

    @property
    def notebook(self) -> Path:
        return self._nb_path

    @property
    def output(self) -> Path:
        return self._output_path

    @field_validator("path_root", mode="before")
    @classmethod
    def _convert_str_to_path(cls, v) -> Path:
        if isinstance(v, str):
            v = Path(v)
        if isinstance(v, Path):
            return v
        raise TypeError

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

    def _output_name(self, config: "Configuration") -> str:
        return Template(self.naming).render(
            name=self._get_name(config=config),
            date=self._get_date(config=config),
            datetime=self._get_datetime(config=config),
            uuid=self._get_uuid(config=config),
            sha=self._get_sha(config=config),
        )

    def _get_notebook_path(self, config: "Configuration") -> Path:
        # create file or folder path
        name = self._output_name(config=config)
        root = Path(self.path_root).resolve()
        root.mkdir(parents=True, exist_ok=True)
        return root / f"{name}.ipynb"

    def resolve_output(self, config: "Configuration") -> Path:
        return self._get_notebook_path(config=config)

    def run(self, config: "Configuration", gen: NotebookNode) -> Path:
        # create file or folder path
        file = self._get_notebook_path(config=config)
        file.write_text(writes(gen))
        self._nb_path = file
        self._output_path = file
        return file

    def generate(self, metadata: dict, config: "Configuration", parent: BaseModel, **kwargs) -> NotebookNode:
        return super().generate(metadata=metadata, config=config, parent=parent, attr="outputs", **kwargs)
