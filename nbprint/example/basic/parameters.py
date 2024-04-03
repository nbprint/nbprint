from pydantic import Field
from typing import Dict, List, Optional

from nbprint.config import Parameters

__all__ = ("ExampleParameters",)


class ExampleParameters(Parameters):
    ticker: str
    a: Optional[int] = 4
    b: Optional[float] = 4.5
    c: List[int] = Field(default=[1, 2, 3])
    d: Dict[str, int] = Field(default={"A": 1, "B": 2, "C": 3})
