import pandas as pd
from typing import Optional

from nbprint import Context

__all__ = ("ExampleContext",)


class ExampleContext(Context):
    df: Optional[pd.DataFrame] = None
