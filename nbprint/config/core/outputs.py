from datetime import date, datetime
from nbformat import NotebookNode, write
from pathlib import Path
from pydantic import DirectoryPath, Field, field_validator
from strenum import StrEnum
from typing import TYPE_CHECKING, List, Literal, Optional, Union
from uuid import uuid4

from ..base import BaseModel, Role

if TYPE_CHECKING:
    from .config import Configuration

__all__ = ("OutputNaming", "Outputs", "NBConvertOutputs")


class OutputNaming(StrEnum):
    name = "${name}"
    date = "${date}"
    datetime = "${datetime}"
    uuid = "${uuid}"
    sha = "${sha}"


class Outputs(BaseModel):
    path_root: DirectoryPath
    naming: List[Union[OutputNaming, str]] = [OutputNaming.name, "-", OutputNaming.date]

    tags: List[str] = Field(default=["nbprint:outputs"])
    role: Role = Role.OUTPUTS
    ignore: bool = True

    @field_validator("path_root", pre=True)
    def convert_str_to_path(cls, v):
        if isinstance(v, str):
            v = Path(v)
        if isinstance(v, Path):
            v.resolve().mkdir(parents=True, exist_ok=True)
            return v
        raise TypeError

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_root = self.path_root.resolve()
        self.path_root.mkdir(parents=True, exist_ok=True)

    def _get_name(self, config: "Configuration") -> str:
        return config.name

    def _get_date(self, config: "Configuration") -> str:
        return date.today().isoformat()

    def _get_datetime(self, config: "Configuration") -> str:
        return datetime.now().isoformat()

    def _get_uuid(self, config: "Configuration") -> str:
        return uuid4()

    def _get_sha(self, config: "Configuration") -> str:
        import hashlib

        m = hashlib.sha256(config.model_dump_json(by_alias=True))
        m.update(config)
        return m.hexdigest()

    def run(self, config: "Configuration", gen: NotebookNode) -> Path:
        # create file or folder path
        file = str(
            Path(self.path_root).resolve()
            / ("".join([x.value if isinstance(x, OutputNaming) else x for x in self.naming]) + ".ipynb")
        )

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

        with open(file, "w") as fp:
            write(gen, fp)
        return file

    def generate(
        self, metadata: dict, config: "Configuration", parent: BaseModel, attr: str = "", *args, **kwargs
    ) -> NotebookNode:
        return super().generate(metadata=metadata, config=config, parent=parent, attr="outputs", *args, **kwargs)


class NBConvertOutputs(Outputs):
    target: Optional[Literal["ipynb", "html", "pdf"]] = "html"  # TODO nbconvert types
    template: Optional[str] = "nbprint"

    def run(self, config: "Configuration", gen: NotebookNode) -> Path:
        from nbconvert.nbconvertapp import main

        notebook = super().run(config=config, gen=gen)
        main([notebook, f"--to={self.target}", f"--template={self.template}", "--execute"])


# class PapermillOutputs(NBConvertOutputs):
#     def run(self, config: "Configuration", gen: NotebookNode) -> Path:
#         from nbconvert.nbconvertapp import main

#         notebook = super().run(config=config, gen=gen)
#         main([notebook, f"--to={self.target}", f"--template={self.template}", "--execute"])
