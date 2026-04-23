"""IPython cell magic for annotating cells with nbprint metadata.

Usage inside a notebook cell::

    %%nbprint section=frontmatter css=":scope { font-size: 18px; }"
    display(Markdown("# Introduction"))

The magic line is parsed as ``key=value`` pairs.  Recognised keys:
``section``, ``css``, ``classname``, ``ignore``.  The metadata is emitted
as a custom MIME-type output identical to ``NBPrintCell``.
"""

from __future__ import annotations

import shlex

from IPython.core.magic import Magics, cell_magic, magics_class

from .cell import NBPrintCell

__all__ = ("NBPrintMagics", "load_ipython_extension")

_BOOL_TRUTHY = frozenset({"true", "1", "yes"})
_BOOL_FALSY = frozenset({"false", "0", "no"})


def _parse_magic_line(line: str) -> dict:
    """Parse ``key=value`` pairs from the magic line."""
    tokens = shlex.split(line)
    kwargs: dict = {}
    for token in tokens:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key == "ignore":
            kwargs[key] = value.lower() in _BOOL_TRUTHY
        else:
            kwargs[key] = value
    return kwargs


@magics_class
class NBPrintMagics(Magics):
    @cell_magic
    def nbprint(self, line: str, cell: str):  # noqa: ANN201
        """``%%nbprint`` cell magic — emit nbprint metadata then run cell."""
        kwargs = _parse_magic_line(line)
        NBPrintCell(**kwargs)
        # Execute the rest of the cell
        self.shell.run_cell(cell)


def load_ipython_extension(ipython) -> None:
    """Register the ``%%nbprint`` magic when loaded as an extension."""
    ipython.register_magics(NBPrintMagics)
