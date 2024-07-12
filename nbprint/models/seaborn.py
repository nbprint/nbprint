from __future__ import annotations

from IPython.display import HTML
from pydantic import Field
from typing import Literal

from nbprint import Content

__all__ = ("SeabornDisplayConfiguration",)


class SeabornDisplayConfiguration(Content):
    """Class to configure Seaborn global configuration."""

    style: Literal["white", "dark", "whitegrid", "darkgrid", "ticks"] = Field(default="whitegrid")
    context: Literal["paper", "notebook", "talk", "poster"] = Field(default="notebook")
    palette: str | list[str] = Field(default="tab10")

    def __call__(self, *_, **__) -> HTML:
        """Configure Seaborn global configuration."""
        import seaborn as sns

        sns.set_theme(self.context, self.style, self.palette)
        return HTML("")
