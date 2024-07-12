from __future__ import annotations

import pandas as pd

from nbprint import Context

__all__ = ("ExampleContext",)


class ExampleContext(Context):
    string: str = ""
    df: pd.DataFrame | None = None
