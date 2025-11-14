import os

from IPython.display import HTML

from nbprint import Content

__all__ = ("PlotlyRendererConfiguration",)


class PlotlyRendererConfiguration(Content):
    default: str | None = "notebook_connected"

    def __call__(self, **_) -> HTML:
        if os.environ.get("_NBPRINT_IN_NBCONVERT", "0") == "1":
            import plotly.io as pio

            pio.renderers.default = self.default
        return HTML("")
