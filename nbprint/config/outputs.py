from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from nbformat import NotebookNode
from pydantic import DirectoryPath, validator

from .base import BaseModel
from .utils import SerializeAsAny

if TYPE_CHECKING:
    from .config import Configuration


class OutputNaming(str, Enum):
    uuid = "uuid"
    sha = "sha"


class Outputs(BaseModel):
    path_root: SerializeAsAny[DirectoryPath]
    naming: SerializeAsAny[OutputNaming]

    @validator("path_root", pre=True)
    def convert_str_to_path(cls, v):
        if isinstance(v, str):
            v = Path(v)
        if isinstance(v, Path):
            v.mkdir(parents=True, exist_ok=True)
            return v
        raise TypeError

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_root.mkdir(parents=True, exist_ok=True)

    def generate(self, metadata: dict = None, config: "Configuration" = None) -> NotebookNode:
        cell = super()._base_generate(metadata=metadata, config=config, attr="outputs")
        cell.metadata.tags.append("nbprint:outputs")
        cell.metadata.nbprint.role = "outputs"
        return cell
