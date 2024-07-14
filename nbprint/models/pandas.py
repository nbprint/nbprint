from __future__ import annotations

from IPython.display import HTML
from pydantic import Field

from nbprint import Content

__all__ = ("PandasDisplayConfiguration",)


class PandasDisplayConfiguration(Content):
    max_columns: int | None = Field(default=None)
    max_rows: int = Field(default=100)

    def __call__(self, *_, **__):
        import pandas as pd

        pd.set_option("display.max_columns", self.max_columns)
        pd.set_option("display.max_rows", self.max_rows)
        return HTML("")
