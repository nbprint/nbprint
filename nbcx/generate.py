from sys import version_info

from nbformat import NotebookNode
from nbformat.v4 import new_notebook

import nbcx

from .config import NBCXConfiguration


def generate(config: NBCXConfiguration) -> NotebookNode:
    nb = new_notebook()
    nb.metadata.nbcx = {}
    nb.metadata.nbcx.version = nbcx.__version__
    nb.metadata.nbcx.tags = []
    nb.metadata.nbcx.language = f"python{version_info.major}.{version_info.minor}"

    base_meta = {
        "tags": [],
        "nbcx": {},
    }

    nb.cells = config.generate(metadata=base_meta, config=config)

    return nb
