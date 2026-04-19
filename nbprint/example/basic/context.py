from typing import Any

import pandas as pd
from pydantic import Field

from nbprint import Context

__all__ = ("ExampleContext",)


class ExampleContext(Context):
    string: str = ""
    df: pd.DataFrame | None = None
    params: dict[str, Any] = Field(default_factory=dict)
