import os
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional
from uuid import uuid4

from ccflow import ResultBase
from jinja2 import Template
from nbformat import NotebookNode, writes
from pydantic import Field, PrivateAttr, field_validator

from nbprint.config.base import BaseModel, Role

if TYPE_CHECKING:
    from .config import Configuration

__all__ = ("NBConvertOutputs", "Outputs")


class Outputs(ResultBase, BaseModel):
    path_root: Path = Field(default=Path.cwd() / "outputs")
    naming: str = Field(default="{{name}}-{{date}}")

    tags: list[str] = Field(default=["nbprint:outputs"])
    role: Role = Role.OUTPUTS
    ignore: bool = True

    _nb_path: Optional[Path] = PrivateAttr(default=None)
    _output_path: Optional[Path] = PrivateAttr(default=None)

    @property
    def notebook(self) -> Path:
        return self._nb_path

    @property
    def output(self) -> Path:
        return self._output_path

    @field_validator("path_root", mode="before")
    @classmethod
    def convert_str_to_path(cls, v) -> Path:
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

    def _get_notebook_path(self, config: "Configuration") -> Path:
        # create file or folder path
        name = Template(self.naming).render(
            name=self._get_name(config=config),
            date=self._get_date(config=config),
            datetime=self._get_datetime(config=config),
            uuid=self._get_uuid(config=config),
            sha=self._get_sha(config=config),
        )

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


class NBConvertOutputs(Outputs):
    target: Optional[Literal["ipynb", "html", "pdf", "webpdf"]] = "html"  # TODO: nbconvert types
    execute: Optional[bool] = True
    timeout: Optional[int] = 600
    template: Optional[str] = "nbprint"

    @field_validator("target", mode="before")
    @classmethod
    def validate_target(cls, v) -> str:
        if v is None:
            return "html"
        if v == "pdf":
            return "webpdf"
        return v

    def resolve_output(self, config: "Configuration") -> Path:
        # get original notebook
        original = str(super().resolve_output(config=config))
        if self.target == "ipynb":
            return Path(original.replace(".ipynb", ".nbconvert.ipynb"))
        return Path(original.replace(".ipynb", f".{self.target}"))

    def run(self, config: "Configuration", gen: NotebookNode) -> Path:
        from nbconvert.nbconvertapp import main as execute_nbconvert

        # run the nbconvert
        notebook = super().run(config=config, gen=gen)

        cmd = [
            str(notebook),
            f"--to={self.target}",
            f"--template={self.template}",
        ]

        if self.execute:
            cmd.extend(
                [
                    "--execute",
                    f"--ExecutePreprocessor.timeout={self.timeout}",
                ]
            )

        # We have some cheats here because we have to
        os.environ["_NBPRINT_IN_NBCONVERT"] = "1"
        os.environ["PSP_JUPYTER_HTML_EXPORT"] = "1"
        execute_nbconvert(cmd)
        self._output_path = self.resolve_output(config=config)
        return self._output_path


# class PapermillOutputs(NBConvertOutputs):
#     def run(self, config: "Configuration", gen: NotebookNode) -> Path:
#         from nbconvert.nbconvertapp import main

#         notebook = super().run(config=config, gen=gen)
#         main([notebook, f"--to={self.target}", f"--template={self.template}", "--execute"])
