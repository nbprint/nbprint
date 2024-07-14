from pydantic import Field

from nbprint.config import Parameters

# from datetime import datetime
# from typing import Dict, list, Optional


class ExampleFinanceParameters(Parameters):
    ticker: str
    authors: list[str] = Field(default=[])
    color: str
