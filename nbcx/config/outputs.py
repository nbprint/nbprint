from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from nbformat import NotebookNode
from pydantic import DirectoryPath, validator

from .base import NBCXBaseModel
from .utils import SerializeAsAny

if TYPE_CHECKING:
    from .config import NBCXConfiguration


class NBCXOutputNaming(str, Enum):
    uuid = "uuid"
    sha = "sha"


class NBCXOutputs(NBCXBaseModel):
    path_root: SerializeAsAny[DirectoryPath]
    naming: SerializeAsAny[NBCXOutputNaming]

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

    def generate(self, metadata: dict = None, config: "NBCXConfiguration" = None) -> NotebookNode:
        cell = super()._base_generate(metadata=metadata, config=config, attr="outputs")
        cell.metadata.tags.append("nbcx:outputs")
        cell.metadata.nbcx.role = "outputs"
        return cell
