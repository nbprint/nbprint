from typing import Any, Dict, Optional

import pandas as pd
from pydantic import Field

from nbprint import Context

__all__ = ("ExampleContext",)


class ExampleContext(Context):
    string: str = ""
    df: Optional[pd.DataFrame] = None
    params: Dict[str, Any] = Field(default_factory=dict)
