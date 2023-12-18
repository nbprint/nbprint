from sys import version_info

from nbformat import NotebookNode
from nbformat.v4 import new_notebook

import nbprint

from .config import Configuration


def generate(config: Configuration) -> NotebookNode:
    nb = new_notebook()
    nb.metadata.nbprint = {}
    nb.metadata.nbprint.version = nbprint.__version__
    nb.metadata.nbprint.tags = []
    nb.metadata.nbprint.language = f"python{version_info.major}.{version_info.minor}"

    base_meta = {
        "tags": [],
        "nbprint": {},
    }

    nb.cells = config.generate(metadata=base_meta, config=config)

    return nb
