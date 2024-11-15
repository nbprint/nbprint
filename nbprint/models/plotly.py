import os
from typing import Optional

from IPython.display import HTML

from nbprint import Content

__all__ = ("PlotlyRendererConfiguration",)


class PlotlyRendererConfiguration(Content):
    default: Optional[str] = "notebook_connected"

    def __call__(self, **_) -> HTML:
        if os.environ.get("_NBPRINT_IN_NBCONVERT", "0") == "1":
            import plotly.io as pio

            pio.renderers.default = self.default
        return HTML("")
