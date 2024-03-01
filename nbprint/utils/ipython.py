from IPython.display import DisplayObject, display


class DisplayList(DisplayObject):
    def __init__(self, *objs):
        self._objs = objs

    def _repr_html_(self):
        for o in self._objs:
            display(o)
        return ""
