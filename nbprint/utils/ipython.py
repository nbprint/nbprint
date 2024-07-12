"""IPython utilities."""

from IPython.display import DisplayObject, display


class DisplayList(DisplayObject):
    """Class that holds a set of displayable objects."""

    def __init__(self, *objs) -> None:
        """Construct instance from tuple of objects."""
        self._objs = objs

    def _repr_html_(self) -> str:
        """Construct html representation for ipython."""
        for o in self._objs:
            display(o)
        return ""
