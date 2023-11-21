from typing import List, Union

from nbformat import NotebookNode


def _append_or_extend(cells: list, cell_or_cells: Union[NotebookNode, List[NotebookNode]]) -> None:
    if isinstance(cell_or_cells, list):
        cells.extend(cell_or_cells)
    elif cell_or_cells:
        cells.append(cell_or_cells)
    # None, ignore
