from IPython.display import HTML
from pydantic import Field
from typing import Optional

from nbprint import Content

__all__ = ("PandasDisplayConfiguration",)


class PandasDisplayConfiguration(Content):
    max_columns: Optional[int] = Field(default=None)
    max_rows: int = Field(default=100)

    def __call__(self, ctx=None, *args, **kwargs):
        import pandas as pd

        pd.set_option("display.max_columns", self.max_columns)
        pd.set_option("display.max_rows", self.max_rows)
        return HTML("")
