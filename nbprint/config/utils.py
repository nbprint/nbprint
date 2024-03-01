import pydantic
from nbformat import NotebookNode
from packaging.version import Version
from typing import List, Union

if Version(pydantic.__version__) >= Version("2"):
    from pydantic import SerializeAsAny  # noqa: F401
else:

    class SerializeAsAny:
        def __class_getitem__(self, typ):
            return typ


def _append_or_extend(cells: list, cell_or_cells: Union[NotebookNode, List[NotebookNode]]) -> None:
    if isinstance(cell_or_cells, list):
        print(type(cell_or_cells[0]))
        cells.extend(cell_or_cells)
    elif cell_or_cells:
        cells.append(cell_or_cells)
    # None, ignore
