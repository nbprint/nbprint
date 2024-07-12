from __future__ import annotations

from IPython.display import HTML
from pydantic import Field

from nbprint import Content

__all__ = ("PandasDisplayConfiguration",)


class PandasDisplayConfiguration(Content):
    """Class to configure Pandas global configuration."""

    max_columns: int | None = Field(default=None)
    max_rows: int = Field(default=100)

    def __call__(self, *_, **__) -> HTML:
        """Configure Pandas global configuration."""
        import pandas as pd

        pd.set_option("display.max_columns", self.max_columns)
        pd.set_option("display.max_rows", self.max_rows)
        return HTML("")
