from __future__ import annotations

import os
from datetime import date, datetime
from nbformat import NotebookNode, write
from pathlib import Path
from pydantic import DirectoryPath, Field, field_validator
from strenum import StrEnum
from typing import TYPE_CHECKING, Literal
from uuid import uuid4

from nbprint.config.base import BaseModel, Role

if TYPE_CHECKING:
    from .config import Configuration

__all__ = ("OutputNaming", "Outputs", "NBConvertOutputs")


class OutputNaming(StrEnum):
    """Class for output naming scheme."""

    name = "${name}"
    date = "${date}"
    datetime = "${datetime}"
    uuid = "${uuid}"
    sha = "${sha}"


class Outputs(BaseModel):
    """Class that represents the outputs of a report."""

    path_root: DirectoryPath
    naming: list[OutputNaming | str] = Field(default=[OutputNaming.name, "-", OutputNaming.date])

    tags: list[str] = Field(default=["nbprint:outputs"])
    role: Role = Role.OUTPUTS
    ignore: bool = True

    @field_validator("path_root", mode="before")
    @classmethod
    def convert_str_to_path(cls, v) -> Path:
        """Helper to convert string path to a filesystem path."""
        if isinstance(v, str):
            v = Path(v)
        if isinstance(v, Path):
            v.resolve().mkdir(parents=True, exist_ok=True)
            return v
        raise TypeError

    def __init__(self, *args, **kwargs) -> None:
        """Construct an outputs instance."""
        super().__init__(*args, **kwargs)
        self.path_root = self.path_root.resolve()
        self.path_root.mkdir(parents=True, exist_ok=True)

    def _get_name(self, config: Configuration) -> str:
        return config.name

    def _get_date(self, *_, **__) -> str:
        return date.today().isoformat()

    def _get_datetime(self, *_, **__) -> str:
        return datetime.now().isoformat()

    def _get_uuid(self, *_, **__) -> str:
        return uuid4()

    def _get_sha(self, config: Configuration) -> str:
        import hashlib

        m = hashlib.sha256(config.model_dump_json(by_alias=True))
        m.update(config)
        return m.hexdigest()

    def run(self, config: Configuration, gen: NotebookNode) -> Path:
        """Execute an output generator."""
        # create file or folder path
        file = str(Path(self.path_root).resolve() / ("".join([x.value if isinstance(x, OutputNaming) else x for x in self.naming]) + ".ipynb"))

        _pattern_map = {
            OutputNaming.name: self._get_name,
            OutputNaming.date: self._get_date,
            OutputNaming.datetime: self._get_datetime,
            OutputNaming.uuid: self._get_uuid,
            OutputNaming.sha: self._get_sha,
        }
        for pattern in OutputNaming:
            if pattern.value in str(file):
                file = file.replace(pattern.value, _pattern_map[pattern](config))

        with Path(file).resolve().open("w") as fp:
            write(gen, fp)
        return file

    def generate(self, metadata: dict, config: Configuration, parent: BaseModel, *_, **__) -> NotebookNode:
        """Generate cells corresponding to the output. Note, this is usually empty."""
        return super().generate(metadata=metadata, config=config, parent=parent, attr="outputs", counter=None)


class NBConvertOutputs(Outputs):
    """Outputs class that uses NBConvert to execute and convert a notebook to a variety of other output formats."""

    target: Literal["ipynb", "html", "pdf"] = Field(default="html")  # TODO: nbconvert types
    execute: bool = Field(default=True)
    timeout: int = Field(default=600)
    template: str = Field(default="nbprint")

    def run(self, config: Configuration, gen: NotebookNode) -> Path:
        """Execute NBConvert to execute and convert a notebook."""
        from nbconvert.nbconvertapp import main as execute_nbconvert

        # set for convenience
        os.environ["PSP_JUPYTER_HTML_EXPORT"] = "1"

        # run the nbconvert
        notebook = super().run(config=config, gen=gen)

        cmd = [
            notebook,
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

        execute_nbconvert(cmd)


# class PapermillOutputs(NBConvertOutputs):
#     def run(self, config: Configuration, gen: NotebookNode) -> Path:
#         from nbconvert.nbconvertapp import main

#         notebook = super().run(config=config, gen=gen)
#         main([notebook, f"--to={self.target}", f"--template={self.template}", "--execute"])
